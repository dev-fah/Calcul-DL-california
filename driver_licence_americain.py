# driver_license_real_card_with_office.py

import streamlit as st
import datetime, hashlib, random

st.set_page_config(page_title="Permis réaliste", layout="centered")

# -------------------------
# CSS (chargé UNE seule fois)
# -------------------------
st.markdown("""
<style>
.card {
    width: 420px;
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

def rletter(r):
    return r.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def next_fd():
    """Permet d'alterner les codes FD de 10 à 99 à chaque génération"""
    if 'fd_counter' not in st.session_state:
        st.session_state.fd_counter = 10
    val = st.session_state.fd_counter
    st.session_state.fd_counter += 1
    if st.session_state.fd_counter > 99:
        st.session_state.fd_counter = 10
    return val

# -------------------------
# DICTIONNAIRE FIELD OFFICES
# -------------------------
field_offices = {
    "Corte Madera":525,"Daly City":599,"El Cerrito":585,"Fremont":643,"Hayward":521,
    "Los Gatos":641,"Novato":647,"Oakland (Claremont)":501,"Oakland (Coliseum)":604,
    "Pittsburg":651,"Pleasanton":639,"Redwood City":542,"San Francisco":503,
    "San Jose (Alma)":516,"San Jose (Driver License Center)":607,"San Mateo":594,
    "Santa Clara":632,"Vallejo":538,"Arleta":628,"Bellflower":610,"Culver City":514,
    "Glendale":540,"Hollywood":633,"Inglewood":544,"Long Beach":507,"Los Angeles (Hope St)":502,
    "Montebello":531,"Pasadena":510,"Santa Monica":548,"Torrance":592,"West Covina":591,
    "Costa Mesa":627,"Fullerton":547,"Laguna Hills":642,"Santa Ana":529,"San Clemente":652,
    "Westminster":623,"Chula Vista":609,"El Cajon":549,"Oceanside":593,"San Diego (Clairemont)":618,
    "San Diego (Normal St)":504,"San Marcos":637,"San Ysidro":649,"Auburn":533,"Chico":534,
    "Eureka":522,"Redding":550,"Roseville":635,"Sacramento (Broadway)":500,"Sacramento (South)":603,
    "Woodland":535,"Bakersfield":511,"Fresno":505,"Lodi":595,"Modesto":536,"Stockton":517,"Visalia":519
}

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
rstr = st.text_input("Restrictions","NONE")

iss = st.date_input("Émission", datetime.date.today())

office_name = st.selectbox("Bureau Field Office", list(field_offices.keys()))

generate = st.button("Générer")

# -------------------------
# RENDU CARTE
# -------------------------
if generate:
    r = random.Random(seed(ln,fn,dob))
    dl = ln[0].upper() + rdigits(r,7)  # Numéro permis: 1 lettre initiale + 7 chiffres
    exp_year = iss.year + 5
    exp = datetime.date(exp_year, dob.month, dob.day)  # Expiration le jour anniversaire

    fd_num = next_fd()
    dd = f"{iss.strftime('%m/%d/%Y')}{field_offices[office_name]}{fd_num:02d}FD/{iss.year%100:02d}"

    html = f"""
    <div class="card">
        <div class="header">
            <div>CALIFORNIA USA DRIVER LICENSE</div>
            <div class="badge">{dl}</div>
        </div>
        <div class="body">
            <div class="photo"></div>
            <div class="info">
                <div class="label">LN</div>
                <div class="value">{ln}</div>
                <div class="label">FN</div>
                <div class="value">{fn}</div>
                <div class="label">SEX</div>
                <div class="value">{sex}</div>
                <div class="label">DOB</div>
                <div class="value">{dob.strftime('%m/%d/%Y')}</div>
                <div class="label">HGT / WGT</div>
                <div class="value">{h1}'-{h2:02d}'' / {w} lb</div>
                <div class="label">EYES / HAIR</div>
                <div class="value">{eyes} / {hair}</div>
                <div class="label">RSTR</div>
                <div class="value">{rstr}</div>
                <div class="label">DD</div>
                <div class="value">{dd}</div>
                <div class="label">ISS</div>
                <div class="value">{iss.strftime('%m/%d/%Y')}</div>
                <div class="label">EXP</div>
                <div class="value">{exp.strftime('%m/%d/%Y')}</div>
                <div class="label">CLASS</div>
                <div class="value">{cls}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    st.success("Carte générée !")
