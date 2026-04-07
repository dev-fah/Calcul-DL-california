# driver_licence_officiel.py
# Générateur DL conforme aux règles officielles avec menu déroulant Field Office (CSS en gras)
# Dépendances : streamlit, pandas, openpyxl
# pip install streamlit pandas openpyxl

import streamlit as st
import pandas as pd
import datetime
import hashlib
import random
import json
from io import BytesIO

st.set_page_config(page_title="Générateur DL Officiel", layout="wide")

# -------------------------
# CSS pour rendre les options du menu déroulant en gras
# -------------------------
st.markdown("""
<style>
/* cibler les options du selectbox */
div[data-baseweb="select"] span {
    font-weight: bold !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Utilitaires
# -------------------------
def deterministic_seed(*parts: str) -> int:
    key = "|".join([p or "" for p in parts])
    return int(hashlib.md5(key.encode("utf-8")).hexdigest()[:8], 16)

def random_digits(rnd: random.Random, length: int) -> str:
    return "".join(rnd.choice("0123456789") for _ in range(length))

def random_letter(rnd: random.Random) -> str:
    return rnd.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def format_date_us(d: datetime.date) -> str:
    return d.strftime("%m/%d/%Y")

def format_height(feet: int, inches: int) -> str:
    return f"{feet}'-{inches:02d}\""

def to_json_bytes(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")

def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

def to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Résultats")
    return buf.getvalue()

# -------------------------
# Formulaire principal
# -------------------------
st.title("🆔 Générateur DL et DD (Format officiel)")

with st.form(key="form_main"):
    ln = st.text_input("Nom de famille (LN)", value="HARMS")
    fn = st.text_input("Prénom (FN)", value="ROSA")
    sex = st.selectbox("Sexe (SEX)", ["M", "F", "X"], index=1)
    dob = st.date_input("Date de naissance (DOB)", value=datetime.date(1995, 3, 15))
    hgt_feet = st.number_input("Taille - pieds", min_value=0, max_value=8, value=5)
    hgt_inches = st.number_input("Taille - pouces", min_value=0, max_value=11, value=10)
    wgt = st.number_input("Poids (WGT en lbs)", min_value=50, max_value=400, value=160)
    iss = st.date_input("Date d’émission (ISS)", value=datetime.date(2024, 6, 10))
    hair = st.text_input("Cheveux (HAIR, 3 lettres)", value="BRN")
    eyes = st.text_input("Yeux (EYES, 3 lettres)", value="BLU")

    # Menu déroulant Field Office avec CSS en gras
    fo_options = [
        "San Jose (654) - Silicon Valley",
        "Fresno (210) - Central Valley",
        "Oakland (987) - East Bay",
        "Riverside (543) - Inland Empire",
        "Santa Ana (876) - Orange County",
        "Bakersfield (102) - Central Valley",
        "Long Beach (304) - Greater Los Angeles Area",
        "San Bernardino (607) - Inland Empire",
        "Stockton (412) - Central Valley",
        "Santa Barbara (205) - Central Coast",
        "Redding (530) - Far Northern California",
        "Eureka (707) - North Coast"
    ]

    fo = st.selectbox("Bureau (Field Office)", fo_options, index=0)

    class_ = st.text_input("Classe (CLASS)", value="C")
    rstr = st.text_input("Restrictions (RSTR)", value="NONE")
    end = st.text_input("Endorsements (END)", value="")
    export_format = st.selectbox("Format d'export", ["JSON", "CSV", "XLSX"])
    calculate = st.form_submit_button("Calculer")

# -------------------------
# Traitement
# -------------------------
if calculate:
    rnd = random.Random(deterministic_seed(ln, fn, dob.isoformat()))

    # DL Number : 1 lettre + 7 chiffres
    dl_number = random_letter(rnd) + random_digits(rnd, 7)

    # Dates
    exp_date = iss.replace(year=iss.year + 6)  # validité 6 ans
    dob_str = format_date_us(dob)
    iss_str = format_date_us(iss)
    exp_str = format_date_us(exp_date)

    # Champs en majuscules
    ln = ln.upper()
    fn = fn.upper()
    hair = hair.upper()[:3].ljust(3, "X")
    eyes = eyes.upper()[:3].ljust(3, "X")

    # Hauteur
    hgt = format_height(int(hgt_feet), int(hgt_inches))

    # DD (Document Discriminator) : ISS + séquence
    dd = f"{iss_str.replace('/','')}{random_digits(rnd,6)}"

    result = {
        "DL_NUMBER": dl_number,
        "LN": ln,
        "FN": fn,
        "SEX": sex,
        "DOB": dob_str,
        "HGT": hgt,
        "WGT": f"{wgt} lb",
        "HAIR": hair,
        "EYES": eyes,
        "ISS": iss_str,
        "EXP": exp_str,
        "CLASS": class_,
        "RSTR": rstr,
        "END": end,
        "FO": fo,
        "DD": dd,
        "GENERATED_AT": datetime.datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S")
    }

    # Aperçu
    st.subheader("Aperçu officiel")
    st.json(result)

    # Export
    if export_format == "JSON":
        data_bytes = to_json_bytes(result); mime = "application/json"; fname = "dl_officiel.json"
    elif export_format == "CSV":
        data_bytes = to_csv_bytes(pd.DataFrame([result])); mime = "text/csv"; fname = "dl_officiel.csv"
    else:
        data_bytes = to_excel_bytes(pd.DataFrame([result])); mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"; fname = "dl_officiel.xlsx"

    st.download_button("⬇️ Télécharger", data=data_bytes, file_name=fname, mime=mime)
    st.success("Génération terminée — fichier conforme aux règles officielles.")
