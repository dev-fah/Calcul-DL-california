# driver_licence_americain.py
# Requirements (requirements.txt):
# streamlit==1.32.0
# fpdf2==2.7.8
# pandas==2.2.1
# openpyxl==3.1.2
# pillow==10.2.0

import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO
import traceback
import logging
import sys

# --- Logging vers stderr pour que Streamlit Cloud capture les logs ---
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration page (doit être appelé avant tout st.* affichage) ---
st.set_page_config(page_title="Calcul DL California", layout="centered")

# --- Fonction utilitaire : génération PDF en bytes (robuste) ---
def export_pdf_bytes(dataframe, title="Résultat du calcul DL"):
    """
    Génère un PDF à partir d'un DataFrame pandas et renvoie des bytes.
    Méthode robuste : gère les retours str/bytes de fpdf.output(dest="S").
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        # Utiliser une police standard disponible
        pdf.set_font("Arial", size=12)

        # Titre centré
        pdf.cell(0, 10, title, ln=True, align="C")
        pdf.ln(6)

        # Calculer largeur de colonne simple en fonction du nombre de colonnes
        ncols = max(1, len(dataframe.columns))
        page_width = 190  # largeur approximative utilisable (A4 marges)
        col_width = max(30, int(page_width / ncols))

        # En-têtes
        for col in dataframe.columns:
            header = str(col)[:30]
            pdf.cell(col_width, 8, header, border=1, align="C")
        pdf.ln()

        # Lignes de données
        for _, row in dataframe.iterrows():
            for item in row:
                text = str(item)
                if len(text) > 40:
                    text = text[:37] + "..."
                pdf.cell(col_width, 8, text, border=1)
            pdf.ln()

        # Récupérer le PDF en mémoire (dest="S" renvoie str ou bytes selon version)
        pdf_out = pdf.output(dest="S")
        if isinstance(pdf_out, bytes):
            pdf_bytes = pdf_out
        else:
            # pdf_out est une str ; encoder en latin-1 pour correspondre à l'encodage PDF
            pdf_bytes = pdf_out.encode("latin-1", errors="replace")

        return pdf_bytes

    except Exception as e:
        logger.exception("Erreur lors de la génération du PDF")
        raise

# --- Interface utilisateur complète ---
def main():
    st.title("Calcul DL California")

    with st.form(key="form_calcul"):
        nom = st.text_input("Nom", value="")
        prenom = st.text_input("Prénom", value="")
        age = st.number_input("Âge", min_value=0, max_value=120, step=1, value=18)
        sexe = st.selectbox("Sexe", ["M", "F", "Autre"])
        submit = st.form_submit_button("Calculer")

    # Choix du format d'export (hors formulaire pour permettre téléchargement après calcul)
    format_export = st.selectbox("Choisir le format d’export", ["CSV", "XLSX", "PDF"])

    if submit:
        try:
            # Construire le DataFrame résultat
            statut = "Valide" if age >= 18 else "Mineur"
            df = pd.DataFrame({
                "Nom": [nom or ""],
                "Prénom": [prenom or ""],
                "Âge": [age],
                "Sexe": [sexe],
                "Statut": [statut]
            })

            st.subheader("Résultat")
            st.dataframe(df)

            # Préparer et proposer le téléchargement selon le format choisi
            if format_export == "CSV":
                csv_bytes = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Télécharger (CSV)",
                    data=csv_bytes,
                    file_name="resultat.csv",
                    mime="text/csv"
                )

            elif format_export == "XLSX":
                xlsx_buffer = BytesIO()
                with pd.ExcelWriter(xlsx_buffer, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Résultats")
                xlsx_data = xlsx_buffer.getvalue()
                st.download_button(
                    label="Télécharger (XLSX)",
                    data=xlsx_data,
                    file_name="resultat.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            elif format_export == "PDF":
                # Générer le PDF en bytes (fonction robuste)
                pdf_bytes = export_pdf_bytes(df, title="Résultat du calcul DL - California")
                st.download_button(
                    label="Télécharger (PDF)",
                    data=pdf_bytes,
                    file_name="resultat.pdf",
                    mime="application/pdf"
                )

        except Exception:
            # Log complet côté serveur
            logger.exception("Erreur lors du traitement du formulaire")
            # Afficher une erreur lisible dans l'interface et la traceback pour debug
            st.error("Une erreur est survenue lors de l'exécution de l'application.")
            st.text("Traceback (dernieres lignes) :")
            st.text(traceback.format_exc())

if __name__ == "__main__":
    main()
