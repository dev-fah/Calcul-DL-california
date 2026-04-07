# driver_license_dd_official.py

import streamlit as st
import streamlit.components.v1 as components
import datetime, hashlib, random
from PIL import Image, ImageDraw
import io

st.set_page_config(page_title="Permis Officiel", layout="centered")

# -------------------------
# FIELD OFFICES
# -------------------------
offices = {
    "San Francisco":503,
    "Oakland (Claremont)":501,
    "San Jose (Alma)":516,
    "San Jose (DLC)":607,
    "Los Angeles (Hope St)":502,
    "Hollywood":633,
    "Santa Ana":529,
    "San Diego (Normal St)":504,
    "Sacramento (Broadway)":500,
    "Fresno":505
}

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
st.title("Permis Californie (DD officiel)")

ln = st.text_input("Nom", "HARMS")
fn = st.text_input("Prénom", "ROSA")
sex = st.selectbox("Sexe", ["M","F","X"])
dob = st.date_input("DOB", datetime.date(1995,12,31))

office_name = st.selectbox("Field Office", list(offices.keys()))
office_code = offices[office_name]

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

    # ID SEQUENCE (2 digits)
    sequence = rdigits(r,2)

    # FD RANDOM (10–99)
    fd_random = random.randint(10,99)

    # YEAR (2 digits)
    year_short = str(iss.year)[-2:]

    # DD FINAL
    dd = f"{format_us(iss)}{office_code}{sequence}/{fd_random}FD/{year_short}"

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
    .label {{font-size:10px;opacity:0.7;}}
    .value {{font-weight:bold;margin-bottom:5px;}}
    </style>

    <div class="card">
        <div class="value">DL {dl}</div>

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
    </html>
    """

    components.html(html, height=260)

    # -------------------------
    # EXPORT PNG
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

    st.download_button("📥 Télécharger PNG", buffer.getvalue(), "permis.png")

    # -------------------------
    # EXPORT PDF
    # -------------------------
    pdf_buffer = io.BytesIO()
    img.save(pdf_buffer, format="PDF")

    st.download_button("📄 Télécharger PDF", pdf_buffer.getvalue(), "permis.pdf")

    st.success("Permis généré avec DD officiel")
