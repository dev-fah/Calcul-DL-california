# driver_licence_americain.py
import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO
import traceback

# --- Configuration page ---
st.set_page_config(page_title="Calcul DL California", layout="centered")

# --- Fonction utilitaire : génération PDF en bytes ---
def export_pdf_bytes(dataframe, title="Résultat du calcul DL"):
    """
    Génère un PDF à partir d'un DataFrame pandas et renvoie les bytes.
    Utilise fpdf2 et renvoie une chaîne d'octets encodée en latin-1.
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        # Police standard (Helvetica est disponible dans fpdf)
        pdf.set_font("Helvetica", size=12)

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

        # Récupérer le PDF en mémoire (dest="S" renvoie une str)
        pdf_str = pdf.output(dest="S")
        # fpdf retourne str; encoder en latin-1 pour obtenir bytes sûrs
        pdf_bytes = pdf_str.encode("latin-1")
        return pdf_bytes

    except Exception:
        # Remonter l'exception pour affichage/debug
        raise

# --- Interface utilisateur ---
st.title("Calcul DL California")

with st.form(key="form_calcul"):
    nom = st.text_input("Nom", value="")
    prenom = st.text_input("Prénom", value="")
    age = st.number_input("Âge", min_value=0, max_value=120, step=1, value=18)
    sexe = st.selectbox("Sexe", ["M", "F", "Autre"])
    submit = st.form_submit_button("Calculer")

# Choix du format d'export (hors formulaire pour permettre téléchargement après calcul)
format_export = st.selectbox("Choisir le format d’export", ["CSV", "XLSX", "PDF"])

# Exécution après soumission
if submit:
    try:
        # Construire le DataFrame résultat
        statut = "Valide" if age >= 18 else "Mineur"
        df = pd.DataFrame({
            "Nom": [nom],
            "Prénom": [prenom],
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
            # Générer le PDF en bytes
            pdf_bytes = export_pdf_bytes(df, title="Résultat du calcul DL - California")
            st.download_button(
                label="Télécharger (PDF)",
                data=pdf_bytes,
                file_name="resultat.pdf",
                mime="application/pdf"
            )

    except Exception:
        # Afficher une erreur lisible dans l'interface et la traceback pour debug
        st.error("Une erreur est survenue lors de l'exécution de l'application.")
        st.text("Traceback (dernieres lignes) :")
        st.text(traceback.format_exc())
