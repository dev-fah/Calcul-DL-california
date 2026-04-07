# driver_license_full_region_office.py

import streamlit as st
import datetime, hashlib, random

st.set_page_config(page_title="Permis réaliste", layout="centered")

# -------------------------
# CSS
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

def next_fd():
    if 'fd_counter' not in st.session_state:
        st.session_state.fd_counter = 10
    val = st.session_state.fd_counter
    st.session_state.fd_counter += 1
    if st.session_state.fd_counter > 99:
        st.session_state.fd_counter = 10
    return val

# -------------------------
# DATA OFFICES COMPLET
# -------------------------
offices = [
("Baie de San Francisco","Corte Madera",525),
("Baie de San Francisco","Daly City",599),
("Baie de San Francisco","El Cerrito",585),
("Baie de San Francisco","Fremont",643),
("Baie de San Francisco","Hayward",521),
("Baie de San Francisco","Los Gatos",641),
("Baie de San Francisco","Novato",647),
("Baie de San Francisco","Oakland (Claremont)",501),
("Baie de San Francisco","Oakland (Coliseum)",604),
("Baie de San Francisco","Pittsburg",651),
("Baie de San Francisco","Pleasanton",639),
("Baie de San Francisco","Redwood City",542),
("Baie de San Francisco","San Francisco",503),
("Baie de San Francisco","San Jose (Alma)",516),
("Baie de San Francisco","San Jose (Driver License Center)",607),
("Baie de San Francisco","San Mateo",594),
("Baie de San Francisco","Santa Clara",632),
("Baie de San Francisco","Vallejo",538),

("Grand Los Angeles","Arleta",628),
("Grand Los Angeles","Bellflower",610),
("Grand Los Angeles","Culver City",514),
("Grand Los Angeles","Glendale",540),
("Grand Los Angeles","Hollywood",633),
("Grand Los Angeles","Inglewood",544),
("Grand Los Angeles","Long Beach",507),
("Grand Los Angeles","Los Angeles (Hope St)",502),
("Grand Los Angeles","Montebello",531),
("Grand Los Angeles","Pasadena",510),
("Grand Los Angeles","Santa Monica",548),
("Grand Los Angeles","Torrance",592),
("Grand Los Angeles","West Covina",591),

("Orange County / Sud","Costa Mesa",627),
("Orange County / Sud","Fullerton",547),
("Orange County / Sud","Laguna Hills",642),
("Orange County / Sud","Santa Ana",529),
("Orange County / Sud","San Clemente",652),
("Orange County / Sud","Westminster",623),

("San Diego & Environs","Chula Vista",609),
("San Diego & Environs","El Cajon",549),
("San Diego & Environs","Oceanside",593),
("San Diego & Environs","San Diego (Clairemont)",618),
("San Diego & Environs","San Diego (Normal St)",504),
("San Diego & Environs","San Marcos",637),
("San Diego & Environs","San Ysidro",649),

("Sacramento / Nord","Auburn",533),
("Sacramento / Nord","Chico",534),
("Sacramento / Nord","Eureka",522),
("Sacramento / Nord","Redding",550),
("Sacramento / Nord","Roseville",635),
("Sacramento / Nord","Sacramento (Broadway)",500),
("Sacramento / Nord","Sacramento (South)",603),
("Sacramento / Nord","Woodland",535),

("Vallée Centrale","Bakersfield",511),
("Vallée Centrale","Fresno",505),
("Vallée Centrale","Lodi",595),
("Vallée Centrale","Modesto",536),
("Vallée Centrale","Stockton",517),
("Vallée Centrale","Visalia",519),
]

# Labels affichés
labels = [f"{r} — {v} ({c})" for r,v,c in offices]

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

selected = st.selectbox("Field Office (Région — Ville — Code)", labels)
index = labels.index(selected)
region, city, office_code = offices[index]

generate = st.button("Générer")

# -------------------------
# GENERATION
# -------------------------
if generate:

    r = random.Random(seed(ln,fn,dob))

    dl = ln[0].upper() + rdigits(r,7)
    exp = datetime.date(iss.year+5, dob.month, dob.day)

    fd = next_fd()
    dd = f"{iss.strftime('%m/%d/%Y')}{office_code}{fd:02d}FD/{iss.year%100:02d}"

    html = f"""
    <div class="card">
        <div class="header">
            <div>CALIFORNIA DL</div>
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

                <div class="label">OFFICE</div>
                <div class="value">{region} - {city} ({office_code})</div>

                <div class="label">DD</div>
                <div class="value">{dd}</div>

                <div class="label">ISS / EXP</div>
                <div class="value">{iss.strftime('%m/%d/%Y')} / {exp.strftime('%m/%d/%Y')}</div>
            </div>
        </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)
    st.success("Carte générée avec Field Office complet")
