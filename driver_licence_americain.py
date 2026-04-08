# streamlit_app.py

import streamlit as st
from datetime import date, datetime
import hashlib, random, io
import pypdf417
from PIL import Image

st.set_page_config(page_title="Permis Californie PDF417", layout="centered")
st.title("Générateur Académique de Permis Californie")
st.write("Système interactif pour générer un permis CA avec code-barres PDF417 (AAMVA)")

# --- Fonction utilitaire ---
def seed(*x):
    return int(hashlib.md5("|".join(map(str,x)).encode()).hexdigest()[:8],16)

def rdigits(r,n):
    return "".join(r.choice("0123456789") for _ in range(n))

def rletter(r, initial):
    return initial.upper() if initial.isalpha() else r.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def next_sequence(r):
    return str(r.randint(10,99))

# --- Formulaire ---
with st.form("dl_form"):
    ln = st.text_input("Nom de famille", "HARMS")
    fn = st.text_input("Prénom", "ROSA")
    sex = st.selectbox("Sexe", ["M","F"])
    dob = st.date_input("Date de naissance", date(1990,1,1))
    
    col1, col2 = st.columns(2)
    with col1:
        h1 = st.number_input("Pieds",0,8,5)
        w = st.number_input("Poids (lb)",30,500,160)
    with col2:
        h2 = st.number_input("Pouces",0,11,10)
        eyes = st.text_input("Yeux","BRN")
    hair = st.text_input("Cheveux","BRN")
    cls = st.text_input("Classe","C")
    rstr = st.text_input("Restrictions","NONE")
    endorse = st.text_input("Endorsements","NONE")
    iss = st.date_input("Date d'émission", date.today())
    
    submit = st.form_submit_button("Générer la carte")

# --- Génération ---
if submit:
    r = random.Random(seed(ln,fn,dob))
    dl = rletter(r, ln[0]) + rdigits(r,7)
    
    exp_year = iss.year + 5
    exp = date(exp_year, dob.month, dob.day)

    # Chaîne AAMVA pour PDF417
    aamva_data = {
        "DCS": ln.upper(),
        "DCT": fn.upper(),
        "DAQ": dl,
        "DBB": dob.strftime("%Y%m%d"),
        "DAJ": "CA"
    }
    raw_string = "".join(f"{k}{v}" for k,v in aamva_data.items())
    
    # Génération PDF417 (pypdf417)
    codes = pypdf417.encode(raw_string)
    image = pypdf417.render_image(codes, scale=3)
    
    # Préparation PNG en mémoire
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    # Affichage Streamlit
    st.image(byte_im, caption="Code-barres PDF417 du permis")
    
    st.download_button(
        label="Télécharger le code-barres (PNG)",
        data=byte_im,
        file_name="ca_pdf417.png",
        mime="image/png"
    )
