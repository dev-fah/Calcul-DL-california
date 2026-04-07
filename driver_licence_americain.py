# driver_license_real_card_WORKING.py

import streamlit as st
import streamlit.components.v1 as components
import datetime, hashlib, random

st.set_page_config(page_title="Permis réaliste", layout="centered")

# -------------------------
# UTILS
# -------------------------
def seed(*x):
    return int(hashlib.md5("|".join(map(str,x)).encode()).hexdigest()[:8],16)

def rdigits(r,n):
    return "".join(r.choice("0123456789") for _ in range(n))

def rletter(r):
    return r.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

# -------------------------
# FORMULAIRE
# -------------------------
st.title("Permis réaliste")

ln = st.text_input("Nom", "HARMS")
fn = st.text_input("Prénom", "ROSA")
sex = st.selectbox("Sexe", ["M","F","X"])
dob = st.date_input("Naissance", datetime.date(1995,3,15))

col1, col2 = st.columns(2)
with col1:
    h1 = st.number_input("Pieds",0,8,5)
    w = st.number_input("Poids",30,500,160)
with col2:
    h2 = st.number_input("Pouces",0,11,10)
    eyes = st.text_input("Yeux","BLU")

hair = st.text_input("Cheveux","BRN")
cls = st.text_input("Classe","C")

iss = st.date_input("Émission", datetime.date.today())

generate = st.button("Générer")

# -------------------------
# CARTE HTML (RENDU RÉEL)
# -------------------------
if generate:

    r = random.Random(seed(ln,fn,dob))
    dl = rletter(r)+rdigits(r,7)
    exp = iss.replace(year=iss.year+6)

    html = f"""
    <html>
    <head>
    <style>
    body {{
        margin:0;
        font-family:Arial;
    }}
    .card {{
        width:420px;
        border-radius:14px;
        padding:16px;
        background: linear-gradient(135deg,#1e3a8a,#2563eb);
        color:white;
        box-shadow:0 10px 30px rgba(0,0,0,0.2);
    }}
    .header {{
        display:flex;
        justify-content:space-between;
        font-weight:700;
        margin-bottom:10px;
    }}
    .body {{
        display:flex;
        gap:10px;
    }}
    .photo {{
        width:90px;
        height:110px;
        background:#ddd;
        border-radius:8px;
    }}
    .label {{
        font-size:10px;
        opacity:0.7;
    }}
    .value {{
        font-weight:700;
        margin-bottom:4px;
    }}
    .footer {{
        display:flex;
        justify-content:space-between;
        margin-top:10px;
        font-size:11px;
    }}
    .badge {{
        background:white;
        color:#1e3a8a;
        padding:2px 6px;
        border-radius:6px;
    }}
    </style>
    </head>

    <body>
        <div class="card">

            <div class="header">
                <div>DRIVER LICENSE</div>
                <div class="badge">{dl}</div>
            </div>

            <div class="body">
                <div class="photo"></div>

                <div>
                    <div class="label">Nom</div>
                    <div class="value">{ln}</div>

                    <div class="label">Prénom</div>
                    <div class="value">{fn}</div>

                    <div class="label">Sexe</div>
                    <div class="value">{sex}</div>

                    <div class="label">Naissance</div>
                    <div class="value">{dob}</div>

                    <div class="label">Taille / Poids</div>
                    <div class="value">{h1}ft{h2} / {w}lb</div>

                    <div class="label">Yeux / Cheveux</div>
                    <div class="value">{eyes} / {hair}</div>
                </div>
            </div>

            <div class="footer">
                <div>
                    <div class="label">Émis</div>
                    <div>{iss}</div>
                </div>
                <div>
                    <div class="label">Expire</div>
                    <div>{exp}</div>
                </div>
                <div>
                    <div class="label">Classe</div>
                    <div>{cls}</div>
                </div>
            </div>

        </div>
    </body>
    </html>
    """

    components.html(html, height=260)

    st.success("Carte générée")
