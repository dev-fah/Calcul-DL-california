# driver_licence_final_streamlit.py

import streamlit as st
import datetime, random, hashlib, io
from PIL import Image
import pypdf417

# -------------------------
# Config Streamlit
# -------------------------
st.set_page_config(page_title="Permis CA PDF417", layout="centered")
st.title("Générateur officiel de permis California (Académique)")

# -------------------------
# CSS pour la carte
# -------------------------
st.markdown("""
<style>
.card {
    width: 450px;
    border-radius: 14px;
    padding: 16px;
    background: linear-gradient(135deg,#1e3a8a,#2563eb);
    color: white;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    margin: auto;
}
.header {
    display:flex;
    justify-content:space-between;
    align-items:center;
    font-weight:700;
    font-size:14px;
    margin-bottom:10px;
}
.body {
    display:flex;
    gap:12px;
}
.photo {
    width:90px;
    height:110px;
    background:#e5e7eb;
    border-radius:8px;
}
.info {
    flex:1;
    font-size:12px;
}
.label {
    opacity:0.7;
    font-size:10px;
}
.value {
    font-weight:700;
    margin-bottom:4px;
}
.footer {
    margin-top:10px;
    display:flex;
    justify-content:space-between;
    font-size:11px;
}
.badge {
    background:white;
    color:#1e3a8a;
    padding:2px 6px;
    border-radius:6px;
    font-weight:700;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Utilitaires
# -------------------------
def seed(*x):
    return int(hashlib.md5("|".join(map(str,x)).encode()).hexdigest()[:8],16)

def rdigits(r,n):
    return "".join(r.choice("0123456789") for _ in range(n))

def rletter(r, initial):
    return initial.upper() if initial.isalpha() else r.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def next_sequence(r):
    return str(r.randint(10,99))

# -------------------------
# FORMULAIRE DL
# -------------------------
with st.form("dl_form"):
    ln = st.text_input("Nom de famille", "HARMS")
    fn = st.text_input("Prénom", "ROSA")
    sex = st.selectbox("Sexe", ["M","F"])
    dob = st.date_input("Date de naissance", datetime.date(1990,1,1))
    
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
    iss = st.date_input("Date d'émission", datetime.date.today())
    
    dl_num = st.text_input("Numéro de permis (DAQ)", "I1234567")
    
    submit = st.form_submit_button("Générer la carte")

if submit:
    r = random.Random(seed(ln,fn,dob))
    
    # Dates
    exp_year = iss.year + 5
    exp = datetime.date(exp_year, dob.month, dob.day)
    
    # DD simplifié (Field Office + sequence)
    office_code = "500"  # Placeholder pour Field Office
    seq = next_sequence(r)
    dd = f"{iss.strftime('%m/%d/%Y')}{office_code}{seq}FD/{iss.year%100}"
    
    # Carte HTML
    html = f"""
    <div class="card">
        <div class="header">
            <div>CALIFORNIA USA DRIVER LICENSE</div>
            <div class="badge">{dl_num}</div>
        </div>
        <div class="body">
            <div class="photo"></div>
            <div class="info">
                <div class="label">Nom</div><div class="value">{ln}</div>
                <div class="label">Prénom</div><div class="value">{fn}</div>
                <div class="label">Sexe</div><div class="value">{sex}</div>
                <div class="label">DOB</div><div class="value">{dob.strftime('%m/%d/%Y')}</div>
                <div class="label">DD</div><div class="value">{dd}</div>
                <div class="label">ISS</div><div class="value">{iss.strftime('%m/%d/%Y')}</div>
                <div class="label">EXP</div><div class="value">{exp.strftime('%m/%d/%Y')}</div>
                <div class="label">Classe</div><div class="value">{cls}</div>
                <div class="label">Restrictions</div><div class="value">{rstr}</div>
                <div class="label">Endorsements</div><div class="value">{endorse}</div>
                <div class="label">Yeux / Cheveux / Taille / Poids</div>
                <div class="value">{eyes} / {hair} / {h1}'{h2}'' / {w} lb</div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    
    # -------------------------
    # Génération PDF417
    # -------------------------
    dob_fmt = dob.strftime("%Y%m%d")
    raw_data = f"DCS{ln.upper()}DCT{fn.upper()}DAQ{dl_num.upper()}DBB{dob_fmt}"
    
    codes = pypdf417.encode(raw_data, columns=10)
    img = pypdf417.render_image(codes, scale=3)
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue(), caption=f"PDF417 : {raw_data}")
    
    st.download_button("Télécharger le code-barres (PNG)", data=buf.getvalue(), file_name="ca_barcode.png", mime="image/png")
