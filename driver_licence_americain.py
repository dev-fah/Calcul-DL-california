import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO

# --- Fonction d'export PDF ---
def export_pdf(dataframe, filename="resultat.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Titre
    pdf.cell(200, 10, txt="Résultat du calcul DL", ln=True, align="C")
    pdf.ln(10)

    # Tableau des données
    for col in dataframe.columns:
        pdf.cell(60, 10, col, border=1)
    pdf.ln()

    for _, row in dataframe.iterrows():
        for item in row:
            pdf.cell(60, 10, str(item), border=1)
        pdf.ln()

    # Sauvegarde en mémoire
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# --- Interface Streamlit ---
st.title("Calcul DL California")

# Exemple de formulaire
nom = st.text_input("Nom")
age = st.number_input("Âge", min_value=16, max_value=100, step=1)

# Choix du format d’export
format_export = st.selectbox(
    "Choisir le format d’export",
    ["CSV", "XLSX", "PDF"]
)

if st.button("Calculer"):
    # Exemple de dataframe résultat
    df = pd.DataFrame({
        "Nom": [nom],
        "Âge": [age],
        "Statut": ["Valide" if age >= 18 else "Mineur"]
    })

    st.write("Résultat :", df)

    if format_export == "CSV":
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Télécharger (CSV)", csv, "resultat.csv", "text/csv")

    elif format_export == "XLSX":
        xlsx_buffer = BytesIO()
        with pd.ExcelWriter(xlsx_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Résultats")
        st.download_button("Télécharger (XLSX)", xlsx_buffer.getvalue(),
                           "resultat.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    elif format_export == "PDF":
        pdf_buffer = export_pdf(df)
        st.download_button("Télécharger (PDF)", pdf_buffer, "resultat.pdf", "application/pdf")
