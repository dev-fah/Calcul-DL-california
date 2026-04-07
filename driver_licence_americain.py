# driver_license_two_sections.py

import streamlit as st
import streamlit.components.v1 as components
import datetime, hashlib, random

st.set_page_config(page_title="Permis Pro", layout="centered")

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
# FORMULAIRE
# -------------------------
st.title("Permis Californie (Structure Pro)")

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

rstr = st.text_input("Restrictions","NONE")

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
    seq = rdigits(r,2)
    fd = random.randint(10,99)
    year_short = str(iss.year)[-2:]
    dd = f"{format_us(iss)}503{seq}/{fd}FD/{year_short}"

    # Formats
    dob_us = format_us(dob)
    iss_us = format_us(iss)
    exp_us = format_us(exp)
    hgt = format_height(hft, hin)

    # -------------------------
    # SECTION 1 (BLEU)
    # -------------------------
    html = f"""
    <html>
    <style>
    body {{margin:0;font-family:Arial;}}
    .card {{
        width:420px;
        padding:15px;
        border-radius:12px;
        background:linear-gradient(135deg,#1e3a8a,#2563eb);
        color:white;
        font-size:12px;
        line-height:1.6;
    }}
    .row {{margin-bottom:4px;}}
    .label {{opacity:0.7;}}
    </style>

    <div class="card">

        <div class="row">DL {dl}</div>
        <div class="row">EXP {exp_us}</div>

        <div class="row">LN {ln}</div>
        <div class="row">FN {fn}</div>
        <div class="row">DOB {dob_us}</div>

        <div class="row">RSTR {rstr}</div>
        <div class="row">SEX {sex}</div>

        <div class="row">HGT {hgt}</div>
        <div class="row">HAIR {hair}</div>
        <div class="row">WGT {wgt} lb</div>
        <div class="row">EYES {eyes}</div>

        <div class="row">DD {dd}</div>
        <div class="row">ISS {iss_us}</div>

    </div>
    </html>
    """

    components.html(html, height=420)

    # -------------------------
    # SECTION 2 (BARCODE DATA)
    # -------------------------
    barcode_data = f"""
CALIFORNIA USA DRIVER LICENSE
DL: {dl}
EXP: {exp_us}
LN: {ln}
FN: {fn}
DOB: {dob_us}
RSTR: {rstr}
SEX: {sex}
HGT: {hgt}
HAIR: {hair}
WGT: {wgt} lb
EYES: {eyes}
DD: {dd}
ISS: {iss_us}
""".strip()

    st.subheader("📋 Données complètes (non modifiable)")

    st.text_area("", barcode_data, height=260, disabled=True)

    st.success("Structure validée (section 1 + section 2)")
