import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO
import traceback

# --- Fonction d'export PDF robuste ---
def export_pdf_bytes(dataframe):
    try:
        pdf = FPDF()
        pdf.add_page()
        # Utiliser une police standard
        pdf.set_font("Helvetica", size=12)

        # Titre
        pdf.cell(0, 10, "Résultat du calcul DL", ln=True, align="C")
        pdf.ln(6)

        # En-têtes de colonne (largeur automatique simple)
        col_width = max(40, int(180 / max(1, len(dataframe.columns))))
        for col in dataframe.columns:
            pdf.cell(col_width, 8, str(col), border=1, align="C")
        pdf.ln()

        # Lignes
        for _, row in dataframe.iterrows():
            for item in row:
                text = str(item)
                # tronquer si trop long pour éviter débordement
                if len(text) > 40:
                    text = text[:37] + "..."
                pdf.cell(col_width, 8, text, border=1)
            pdf.ln()

        # Récupérer le PDF en bytes de façon sûre
        pdf_str = pdf.output(dest="S").encode("latin-1")
        return pdf_str

    except Exception:
        # Retourner l'exception pour debug si nécessaire
        raise

# --- Interface Streamlit ---
st.set_page_config(page_title="Calcul DL California", layout="centered")
st.title("Calcul DL California")

nom = st.text_input("Nom")
age = st.number_input("Âge", min_value=0, max_value=120, step=1)

format_export = st.selectbox("Choisir le format d’export", ["CSV", "XLSX", "PDF"])

if st.button("Calculer"):
    try:
        df = pd.DataFrame({
            "Nom": [nom or ""],
            "Âge": [age],
            "Statut": ["Valide" if age >= 18 else "Mineur"]
        })

        st.write("Résultat :", df)

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
            pdf_bytes = export_pdf_bytes(df)
            st.download_button("Télécharger (PDF)", pdf_bytes, "resultat.pdf", "application/pdf")

    except Exception as e:
        # Afficher l'erreur dans l'interface pour debug rapide
        st.error("Une erreur est survenue lors de l'exécution.")
        st.text(traceback.format_exc())
