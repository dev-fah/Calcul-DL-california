# driver_licence_americain.py
# Requirements (for reference only, pas besoin d'un fichier séparé si tu ne veux pas):
# streamlit==1.32.0
# pandas==2.2.1
# openpyxl==3.1.2
# pillow==10.2.0

import streamlit as st
import pandas as pd
from io import BytesIO
import traceback
from PIL import Image, ImageOps
import base64

st.set_page_config(page_title="Calcul DL California", layout="centered")

def to_excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Résultats")
    return buffer.getvalue()

def get_table_download_link_csv(df: pd.DataFrame, filename: str = "resultat.csv"):
    csv = df.to_csv(index=False).encode("utf-8")
    return csv

def show_sample_layout():
    st.markdown(
        """
        **Mode d'emploi rapide**
        - Remplis le formulaire puis clique sur **Calculer**.
        - Choisis le format d'export (CSV ou XLSX).
        - Télécharge le fichier via le bouton qui apparaît.
        """
    )

def main():
    st.title("Calcul DL California")
    st.caption("Formulaire simple pour calculer le statut et exporter les résultats")

    # Aide / exemple
    with st.expander("Aide et exemple"):
        show_sample_layout()
        st.write("Exemple de données : Nom, Prénom, Âge, Sexe → Statut (Valide/Mineur)")

    # Formulaire principal
    with st.form(key="form_calcul"):
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom", value="")
            prenom = st.text_input("Prénom", value="")
        with col2:
            age = st.number_input("Âge", min_value=0, max_value=120, step=1, value=18)
            sexe = st.selectbox("Sexe", ["M", "F", "Autre"])

        # Optionnel : upload d'une photo (utilise pillow)
        photo = st.file_uploader("Photo (optionnelle, JPG/PNG)", type=["jpg", "jpeg", "png"])
        submit = st.form_submit_button("Calculer")

    # Formats disponibles
    format_export = st.selectbox("Choisir le format d’export", ["CSV", "XLSX"])

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

            # Afficher la photo si fournie (prévisualisation simple)
            if photo is not None:
                try:
                    image = Image.open(photo)
                    # Petite transformation pour l'affichage (carré, bord)
                    image = ImageOps.exif_transpose(image)
                    image = ImageOps.fit(image, (240, 240))
                    st.image(image, caption="Photo fournie", use_column_width=False)
                except Exception:
                    st.warning("Impossible d'afficher l'image fournie.")

            # Boutons de téléchargement
            if format_export == "CSV":
                csv_bytes = get_table_download_link_csv(df)
                st.download_button(
                    label="Télécharger (CSV)",
                    data=csv_bytes,
                    file_name="resultat.csv",
                    mime="text/csv"
                )

            elif format_export == "XLSX":
                xlsx_bytes = to_excel_bytes(df)
                st.download_button(
                    label="Télécharger (XLSX)",
                    data=xlsx_bytes,
                    file_name="resultat.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            # Afficher un petit résumé
            st.success(f"Calcul effectué — statut : **{statut}**")

        except Exception:
            st.error("Une erreur est survenue lors de l'exécution.")
            st.text(traceback.format_exc())

if __name__ == "__main__":
    main()
