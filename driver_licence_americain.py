# driver_license_official_export.py

import streamlit as st
import streamlit.components.v1 as components
import datetime, hashlib, random
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="Permis Officiel", layout="centered")

# -------------------------
# UTILS
# -------------------------
def seed(*x):
    return int(hashlib.md5("|".join(map(str,x)).encode()).hexdigest()[:8],16)

def rdigits(r,n):
    return "".join(r.choice("0123456789") for _ in range(n))

def format_us(d):
    return d.strftime("%m/%d/%Y")

# -------------------------
# FORMULAIRE
# -------------------------
st.title("Permis Californie (version réaliste)")

ln = st.text_input("Nom", "HARMS")
fn = st.text_input("Prénom", "ROSA")
sex = st.selectbox("Sexe", ["M","F","X"])
dob = st.date_input("Date de naissance", datetime.date(1995,12,31))

iss = st.date_input("Date émission", datetime.date.today())

generate = st.button("Générer")

# -------------------------
# GENERATION LOGIQUE
# -------------------------
if generate:

    r = random.Random(seed(ln,fn,dob))

    # DL NUMBER
    dl = ln[0].upper() + rdigits(r,7)

    # EXP = +5 ans + anniversaire
    exp_year = iss.year + 5
    exp = datetime.date(exp_year, dob.month, dob.day)

    # DD
    dd = f"{format_us(iss)}{rdigits(r,5)}/{rdigits(r,2)}FD/{str(iss.year)[-2:]}"

    dob_us = format_us(dob)
    iss_us = format_us(iss)
    exp_us = format_us(exp)

    # -------------------------
    # HTML CARD
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
    }}
    .title {{
        display:flex;
        justify-content:space-between;
        font-weight:bold;
    }}
    .section {{margin-top:10px; font-size:12px;}}
    .label {{opacity:0.7; font-size:10px;}}
    .value {{font-weight:bold;}}
    </style>

    <div class="card">

        <div class="title">
            <div>CALIFORNIA DL</div>
            <div>{dl}</div>
        </div>

        <div class="section">
            <div class="label">NAME</div>
            <div class="value">{ln} {fn}</div>

            <div class="label">SEX</div>
            <div class="value">{sex}</div>

            <div class="label">DOB</div>
            <div class="value">{dob_us}</div>

            <div class="label">ISS</div>
            <div class="value">{iss_us}</div>

            <div class="label">EXP</div>
            <div class="value">{exp_us}</div>

            <div class="label">DD</div>
            <div class="value">{dd}</div>
        </div>

    </div>
    </html>
    """

    components.html(html, height=260)

    # -------------------------
    # IMAGE PNG
    # -------------------------
    img = Image.new("RGB", (600,300), "#1e3a8a")
    draw = ImageDraw.Draw(img)

    text = f"""
DL: {dl}
NAME: {ln} {fn}
SEX: {sex}
DOB: {dob_us}
ISS: {iss_us}
EXP: {exp_us}
DD: {dd}
"""

    draw.text((20,20), text, fill="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")

    st.download_button(
        "📥 Télécharger PNG",
        data=buffer.getvalue(),
        file_name="permis.png",
        mime="image/png"
    )

    # -------------------------
    # PDF
    # -------------------------
    pdf_buffer = io.BytesIO()
    img.save(pdf_buffer, format="PDF")

    st.download_button(
        "📄 Télécharger PDF",
        data=pdf_buffer.getvalue(),
        file_name="permis.pdf",
        mime="application/pdf"
    )

    st.success("Permis généré + export prêt")
