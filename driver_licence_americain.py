# driver_licence_americain.py
# Paquets utilisés (pour info) : streamlit, pandas, openpyxl, pillow
# Si tu veux tester localement : pip install streamlit pandas openpyxl pillow

import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image, ImageOps
import traceback
import datetime

st.set_page_config(page_title="Simulateur DL - Interface", layout="centered")

def to_excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Résultats")
    return buffer.getvalue()

def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

def sample_deterministic_numbers(name: str) -> dict:
    """
    Génère des valeurs simulées déterministes à partir d'une chaîne.
    Utile pour préremplir certains champs (ex: numéro simulé).
    """
    seed = sum(ord(c) for c in (name or ""))
    return {
        "DL_NUMBER": f"{(seed % 900000) + 100000}",
        "ISSUE_ID": f"{(seed % 9000) + 1000}"
    }

def format_height(feet: int, inches: int) -> str:
    return f"{feet}'-{inches:02d}''"

def main():
    st.title("Simulateur de permis - Interface de saisie")
    st.caption("Survolez les labels pour voir une définition brève. Les numéros générés sont des simulations déterministes pour usage académique.")

    # Exemple d'en-tête / instructions
    with st.expander("Aide rapide"):
        st.markdown(
            "- Remplis les champs ci‑dessous.\n"
            "- Les champs marqués * sont optionnels.\n"
            "- Clique sur **Générer** pour voir le résultat et télécharger en CSV/XLSX."
        )

    # Colonne principale du formulaire
    with st.form(key="form_dl"):
        col1, col2 = st.columns([2, 1])

        with col1:
            ln = st.text_input("Nom de famille (LN)", value="Harms", help="Last Name - Nom de famille")
            fn = st.text_input("Prénom (FN)", value="Rosa", help="First Name - Prénom")
            sex = st.selectbox("Sexe (SEX)", ["M", "F", "Autre"], index=0, help="Sexe tel qu'indiqué")
            dob = st.date_input("Date de naissance (DOB, YYYY-MM-DD)", value=datetime.date(1990, 12, 31), help="Format YYYY-MM-DD")
            wgt = st.text_input("Poids (WGT)", value="175 lb", help="Poids en livres (ex: 175 lb)")
            hgt_feet = st.number_input("Taille - pieds", min_value=0, max_value=8, value=5, help="Pieds pour la taille")
            hgt_inches = st.number_input("Taille - pouces", min_value=0, max_value=11, value=8, help="Pouces pour la taille")
            iss = st.date_input("Date d'émission (ISS, YYYY-MM-DD)", value=datetime.date(2015, 9, 30), help="Date d'émission du permis")
            class_ = st.text_input("Classe (CLASS)", value="C", help="Classe du permis")
            rstr = st.text_input("Restrictions (RSTR)", value="NONE", help="Restrictions éventuelles")
            notes = st.text_area("Notes (optionnel)", value="", help="Commentaires ou remarques (optionnel)")

        with col2:
            st.markdown("### Photo (optionnelle)")
            photo = st.file_uploader("Téléverser une photo (JPG/PNG)", type=["jpg", "jpeg", "png"])
            if photo is not None:
                try:
                    img = Image.open(photo)
                    img = ImageOps.exif_transpose(img)
                    img = ImageOps.fit(img, (300, 300))
                    st.image(img, caption="Aperçu de la photo", use_column_width=False)
                except Exception:
                    st.warning("Impossible d'afficher l'image fournie.")

            st.markdown("---")
            st.markdown("### Génération simulée")
            generated = sample_deterministic_numbers((ln + fn).strip())
            st.text_input("Numéro simulé (DL_NUMBER)", value=generated["DL_NUMBER"], key="dlnum", disabled=True)
            st.text_input("ID émission simulée (ISSUE_ID)", value=generated["ISSUE_ID"], key="issid", disabled=True)

        submit = st.form_submit_button("Générer")

    # Choix du format d'export (après le formulaire)
    format_export = st.selectbox("Choisir le format d’export", ["CSV", "XLSX"])

    if submit:
        try:
            # Construire DataFrame résultat
            hgt = format_height(int(hgt_feet), int(hgt_inches))
            df = pd.DataFrame({
                "LN": [ln or ""],
                "FN": [fn or ""],
                "SEX": [sex],
                "HGT": [hgt],
                "DOB": [dob.isoformat()],
                "WGT": [wgt],
                "ISS": [iss.isoformat()],
                "CLASS": [class_],
                "RSTR": [rstr],
                "DL_NUMBER": [generated["DL_NUMBER"]],
                "ISSUE_ID": [generated["ISSUE_ID"]],
                "NOTES": [notes]
            })

            st.subheader("Aperçu des données générées")
            st.dataframe(df)

            # Téléchargements
            if format_export == "CSV":
                csv_bytes = to_csv_bytes(df)
                st.download_button(
                    label="Télécharger (CSV)",
                    data=csv_bytes,
                    file_name="dl_resultat.csv",
                    mime="text/csv"
                )
            else:
                xlsx_bytes = to_excel_bytes(df)
                st.download_button(
                    label="Télécharger (XLSX)",
                    data=xlsx_bytes,
                    file_name="dl_resultat.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            st.success("Génération terminée — télécharge le fichier si besoin.")
        except Exception:
            st.error("Une erreur est survenue lors de la génération.")
            st.text(traceback.format_exc())

    # Footer / informations
    st.markdown("---")
    st.caption("Interface de démonstration — données simulées pour usage académique uniquement.")

if __name__ == "__main__":
    main()
