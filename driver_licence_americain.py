# driver_licence_americain.py
# Requirements: see requirements.txt

import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO
import traceback

st.set_page_config(page_title="Calcul DL California", layout="centered")

def export_pdf_bytes(dataframe, title="Résultat du calcul DL"):
    pdf = FPDF()
    pdf.add_page()
    # Police standard
    try:
        pdf.set_font("Arial", size=12)
    except Exception:
        pdf.set_font("Helvetica", size=12)
    # Titre
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(6)
    # Calcul largeur colonnes
    ncols = max(1, len(dataframe.columns))
    page_width = 190
    col_width = max(30, int(page_width / ncols))
    # En-têtes
    for col in dataframe.columns:
        pdf.cell(col_width, 8, str(col)[:30], border=1, align="C")
    pdf.ln()
    # Lignes
    for _, row in dataframe.iterrows():
        for item in row:
            text = str(item)
            if len(text) > 40:
                text = text[:37] + "..."
            pdf.cell(col_width, 8, text, border=1)
        pdf.ln()
    # Récupérer le PDF en mémoire
    pdf_out = pdf.output(dest="S")
    if isinstance(pdf_out, bytes):
        return pdf_out
    return pdf_out.encode("latin-1", errors="replace")

def main():
    st.title("Calcul DL California")

    with st.form(key="form_calcul"):
        nom = st.text_input("Nom", value="")
        prenom = st.text_input("Prénom", value="")
        age = st.number_input("Âge", min_value=0, max_value=120, step=1, value=18)
        sexe = st.selectbox("Sexe", ["M", "F", "Autre"])
        submit = st.form_submit_button("Calculer")

    format_export = st.selectbox("Choisir le format d’export", ["CSV", "XLSX", "PDF"])

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
                pdf_bytes = export_pdf_bytes(df, title="Résultat du calcul DL - California")
                st.download_button("Télécharger (PDF)", pdf_bytes, "resultat.pdf", "application/pdf")

        except Exception:
            st.error("Une erreur est survenue lors de l'exécution.")
            st.text(traceback.format_exc())

if __name__ == "__main__":
    main()
