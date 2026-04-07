# driver_license_final.py

import streamlit as st
import datetime, hashlib, random

st.set_page_config(page_title="Permis réaliste CA", layout="centered")

# -------------------------
# CSS (pour la carte)
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
# UTILS
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
# Bureaux Field Office
# -------------------------
offices = {
    "Baie de San Francisco — Corte Madera (525)": 525,
    "Baie de San Francisco — Daly City (599)": 599,
    "Baie de San Francisco — El Cerrito (585)": 585,
    "Baie de San Francisco — Fremont (643)": 643,
    "Baie de San Francisco — Hayward (521)": 521,
    "Baie de San Francisco — Los Gatos (641)": 641,
    "Baie de San Francisco — Novato (647)": 647,
    "Baie de San Francisco — Oakland (Claremont) (501)": 501,
    "Baie de San Francisco — Oakland (Coliseum) (604)": 604,
    "Baie de San Francisco — Pittsburg (651)": 651,
    "Baie de San Francisco — Pleasanton (639)": 639,
    "Baie de San Francisco — Redwood City (542)": 542,
    "Baie de San Francisco — San Francisco (503)": 503,
    "Baie de San Francisco — San Jose (Alma) (516)": 516,
    "Baie de San Francisco — San Jose (Driver License Center) (607)": 607,
    "Baie de San Francisco — San Mateo (594)": 594,
    "Baie de San Francisco — Santa Clara (632)": 632,
    "Baie de San Francisco — Vallejo (538)": 538,
    # Ajouter les autres bureaux selon la liste complète si nécessaire
}

# -------------------------
# FORMULAIRE
# -------------------------
st.title("Générateur de permis de conduire CA")

ln = st.text_input("Nom de famille", "HARMS")
fn = st.text_input("Prénom", "ROSA")
sex = st.selectbox("Sexe", ["M","F","X"])
dob = st.date_input("Date de naissance", datetime.date(1995,3,15))

col1, col2 = st.columns(2)
with col1:
    h1 = st.number_input("Pieds",0,8,5)
    w = st.number_input("Poids (lb)",30,500,160)
with col2:
    h2 = st.number_input("Pouces",0,11,10)
    eyes = st.text_input("Yeux","BLU")
hair = st.text_input("Cheveux","BRN")
cls = st.text_input("Classe","C")
rstr = st.text_input("Restrictions","NONE")
endorse = st.text_input("Endorsements","NONE")
iss = st.date_input("Date d'émission", datetime.date.today())

office_choice = st.selectbox("Field Office", list(offices.keys()))

generate = st.button("Générer la carte")

# -------------------------
# RENDU CARTE
# -------------------------
if generate:
    r = random.Random(seed(ln,fn,dob))
    dl = rletter(r, ln[0]) + rdigits(r,7)
    
    # Date d'expiration : 5 ans après ISS, mais le jour de naissance
    exp_year = iss.year + 5
    exp = datetime.date(exp_year, dob.month, dob.day)
    
    office_code = offices[office_choice]
    seq = next_sequence(r)
    dd = f"{iss.strftime('%m/%d/%Y')}{office_code}{seq}FD/{iss.year%100}"
    
    html = f"""
    <div class="card">
        <div class="header">
            <div>CALIFORNIA USA DRIVER LICENSE</div>
            <div class="badge">{dl}</div>
        </div>
        <div class="body">
            <div class="photo"></div>
            <div class="info">
                <div class="label">Nom</div>
                <div class="value">{ln}</div>
                <div class="label">Prénom</div>
                <div class="value">{fn}</div>
                <div class="label">Sexe</div>
                <div class="value">{sex}</div>
                <div class="label">DOB</div>
                <div class="value">{dob.strftime('%m/%d/%Y')}</div>
                <div class="label">Field Office</div>
                <div class="value">{office_choice}</div>
                <div class="label">DD</div>
                <div class="value">{dd}</div>
                <div class="label">ISS / EXP</div>
                <div class="value">{iss.strftime('%m/%d/%Y')} / {exp.strftime('%m/%d/%Y')}</div>
                <div class="label">Classe</div>
                <div class="value">{cls}</div>
                <div class="label">Restrictions</div>
                <div class="value">{rstr}</div>
                <div class="label">Endorsements</div>
                <div class="value">{endorse}</div>
                <div class="label">Yeux / Cheveux / Taille / Poids</div>
                <div class="value">{eyes} / {hair} / {h1}'-{h2}'' / {w} lb</div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    st.success("Carte générée !")
