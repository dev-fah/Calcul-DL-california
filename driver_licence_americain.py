# driver_license_barcode_data.py

import streamlit as st
import streamlit.components.v1 as components
import datetime, hashlib, random

st.set_page_config(page_title="Permis + Barcode Data", layout="centered")

# -------------------------
# UTILS
# -------------------------
def seed(*x):
    return int(hashlib.md5("|".join(map(str,x)).encode()).hexdigest()[:8],16)

def rdigits(r,n):
    return "".join(r.choice("0123456789") for _ in range(n))

def format_us(d):
    return d.strftime("%m/%d/%Y")

def format_height(ft, inch):
    return f"{ft}'-{str(inch).zfill(2)}''"

# -------------------------
# FORM
# -------------------------
st.title("Permis Californie + Données Code-Barres")

ln = st.text_input("Nom", "HARMS")
fn = st.text_input("Prénom", "ROSA")
sex = st.selectbox("Sexe", ["M","F","X"])
dob = st.date_input("DOB", datetime.date(1995,12,31))

col1, col2 = st.columns(2)
with col1:
    hft = st.number_input("Taille (ft)",0,8,5)
    wgt = st.number_input("Poids",30,500,175)
with col2:
    hin = st.number_input("Taille (inch)",0,11,8)
    eyes = st.text_input("Yeux","BRN")

hair = st.text_input("Cheveux","BRN")

address = st.text_input("Adresse",
"2570 24TH STREET, SACRAMENTO, CA 95818")

cls = st.text_input("Classe","C")
rstr = st.text_input("Restrictions","NONE")
end = st.text_input("Endorsements","NONE")

iss = st.date_input("ISS", datetime.date.today())

generate = st.button("Générer")

# -------------------------
# GENERATION
# -------------------------
if generate:

    r = random.Random(seed(ln,fn,dob))

    # DL
    dl = ln[0].upper() + rdigits(r,7)

    # EXP
    exp = datetime.date(iss.year + 5, dob.month, dob.day)

    # DD
    sequence = rdigits(r,2)
    fd = random.randint(10,99)
    year_short = str(iss.year)[-2:]
    dd = f"{format_us(iss)}503{sequence}/{fd}FD/{year_short}"

    # Formats
    dob_us = format_us(dob)
    iss_us = format_us(iss)
    exp_us = format_us(exp)
    hgt = format_height(hft, hin)

    # -------------------------
    # DATA BARCODE (IMPORTANT)
    # -------------------------
    barcode_data = f"""
CALIFORNIA USA DRIVER LICENSE
DL: {dl}
EXP: {exp_us}
LN: {ln}
FN: {fn}
DOB: {dob_us}
ISS: {iss_us}
DD: {dd}
ADDRESS: {address}
SEX: {sex}
HAIR: {hair}
EYES: {eyes}
HGT: {hgt}
WGT: {wgt} lb
CLASS: {cls}
RSTR: {rstr}
END: {end}
DONOR
""".strip()

    # -------------------------
    # CARTE
    # -------------------------
    html = f"""
    <html>
    <style>
    body {{font-family:Arial;margin:0;}}
    .card {{
        width:420px;
        padding:15px;
        border-radius:12px;
        background:#1e3a8a;
        color:white;
    }}
    .value {{font-weight:bold;margin-bottom:6px;}}
    </style>

    <div class="card">
        <div class="value">DL {dl}</div>
        <div class="value">{ln} {fn}</div>
        <div class="value">DOB {dob_us}</div>
        <div class="value">EXP {exp_us}</div>
    </div>
    </html>
    """

    components.html(html, height=200)

    # -------------------------
    # BARCODE DATA DISPLAY
    # -------------------------
    st.subheader("📋 Données pour Code-Barres")

    st.text_area("Copier pour encoder (PDF417)", barcode_data, height=300)

    st.success("Données prêtes pour génération code-barres")
