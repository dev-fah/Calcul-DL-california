# driver_license_full_offices.py

import streamlit as st
import streamlit.components.v1 as components
import datetime, hashlib, random

st.set_page_config(page_title="Permis Officiel", layout="centered")

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

# Création affichage menu
office_labels = [f"{r} — {v} ({c})" for r,v,c in offices]

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
st.title("Permis Californie (Full Offenses)")

ln = st.text_input("Nom", "HARMS")
fn = st.text_input("Prénom", "ROSA")
sex = st.selectbox("Sexe", ["M","F","X"])
dob = st.date_input("DOB", datetime.date(1995,12,31))

selected = st.selectbox("Field Office", office_labels)
index = office_labels.index(selected)
region, city, office_code = offices[index]

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

    # sequence (2 digits)
    sequence = rdigits(r,2)

    # FD random
    fd = random.randint(10,99)

    # year short
    year_short = str(iss.year)[-2:]

    # DD
    dd = f"{format_us(iss)}{office_code}{sequence}/{fd}FD/{year_short}"

    dob_us = format_us(dob)
    iss_us = format_us(iss)
    exp_us = format_us(exp)

    # -------------------------
    # CARD
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

        <div class="label">OFFICE</div>
        <div class="value">{city} ({office_code})</div>

        <div class="label">DD</div>
        <div class="value">{dd}</div>
    </div>
    </html>
    """

    components.html(html, height=300)

    st.success("Permis généré avec tous les Field Offices")
