# driver_licence_americain.py
# Requirements: see requirements.txt

import streamlit as st
import pandas as pd
from io import BytesIO
import traceback

# Essayer d'importer fpdf; si absent, on gère proprement
try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except Exception:
    FPDF = None
    PDF_AVAILABLE = False

st.set_page_config(page_title="Calcul DL California", layout="centered")

def export_pdf_bytes(dataframe, title="Résultat du calcul DL"):
    """
    Génère un PDF en bytes si fpdf est disponible.
    Lève une exception si fpdf n'est pas installé.
    """
    if not PDF_AVAILABLE:
        raise RuntimeError("fpdf non disponible. Installez fpdf2 dans requirements.txt")

    pdf = FPDF()
    pdf.add_page()
    # Choix de police avec fallback
    try:
        pdf.set_font("Arial", size=12)
    except Exception:
        pdf.set_font("Helvetica", size=12)

    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(6)

    ncols = max(1, len(dataframe.columns))
    page_width = 190
    col_width = max(30, int(page_width / ncols))

    for col in dataframe.columns:
        pdf.cell(col_width, 8, str(col)[:30], border=1, align="C")
    pdf.ln()

    for _, row in dataframe.iterrows():
        for item in row:
            text = str(item)
            if len(text) > 40:
                text = text[:37] + "..."
            pdf.cell(col_width, 8, text, border=1)
        pdf.ln()

    pdf_out = pdf.output(dest="S")
    if isinstance(pdf_out, bytes):
        return pdf_out
    return pdf_out.encode("latin-1", errors="replace")

def main():
    st.title("Calcul DL California")

    if not PDF_AVAILABLE:
        st.warning("Export PDF désactivé — la dépendance fpdf2 n'est pas installée. "
                   "Ajoute 'fpdf2==2.7.8' dans requirements.txt et redeploy si tu veux activer le PDF.")

    with st.form(key="form_calcul"):
        nom = st.text_input("Nom", value="")
        prenom = st.text_input("Prénom", value="")
        age = st.number_input("Âge", min_value=0, max_value=120, step=1, value=18)
        sexe = st.selectbox("Sexe", ["M", "F", "Autre"])
        submit = st.form_submit_button("Calculer")

    # Construire la liste des formats disponibles dynamiquement
    formats = ["CSV", "XLSX"]
    if PDF_AVAILABLE:
        formats.append("PDF")

    format_export = st.selectbox("Choisir le format d’export", formats)

    if submit:
        try:
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

            if format_export == "CSV":
                csv_bytes = df.to_csv(index=False).encode("utf-8")
                st.download_button("Télécharger (CSV)", csv_bytes, "resultat.csv", "text/csv")

            elif format_export == "XLSX":
                xlsx_buffer = BytesIO()
                with pd.ExcelWriter(xlsx_buffer, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Résultats")
                st.download_button("Télécharger (XLSX)", xlsx_buffer.getvalue(),
                                   "resultat.xlsx",
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            elif format_export == "PDF":
                # Sécurité: vérifier encore la disponibilité
                if not PDF_AVAILABLE:
                    st.error("PDF non disponible. Installez fpdf2 et redeploy.")
                else:
                    pdf_bytes = export_pdf_bytes(df, title="Résultat du calcul DL - California")
                    st.download_button("Télécharger (PDF)", pdf_bytes, "resultat.pdf", "application/pdf")

        except Exception:
            st.error("Une erreur est survenue lors de l'exécution.")
            st.text(traceback.format_exc())

if __name__ == "__main__":
    main()
