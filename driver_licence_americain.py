# driver_license_final_full.py

import streamlit as st
import datetime, random, hashlib, re
from datetime import datetime as dt

# ==========================
# Page Streamlit
# ==========================
st.set_page_config(page_title="Permis CA", layout="centered")

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

# ==========================
# Utilitaires
# ==========================
def seed(*x):
    return int(hashlib.md5("|".join(map(str,x)).encode()).hexdigest()[:8],16)

def rdigits(r,n):
    return "".join(r.choice("0123456789") for _ in range(n))

def rletter(r, initial):
    return initial.upper() if initial.isalpha() else r.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def next_sequence(r):
    return str(r.randint(10,99))

# ==========================
# Bureaux Field Office complets
# ==========================
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
    "Grand Los Angeles — Arleta (628)": 628,
    "Grand Los Angeles — Bellflower (610)": 610,
    "Grand Los Angeles — Culver City (514)": 514,
    "Grand Los Angeles — Glendale (540)": 540,
    "Grand Los Angeles — Hollywood (633)": 633,
    "Grand Los Angeles — Inglewood (544)": 544,
    "Grand Los Angeles — Long Beach (507)": 507,
    "Grand Los Angeles — Los Angeles (Hope St) (502)": 502,
    "Grand Los Angeles — Montebello (531)": 531,
    "Grand Los Angeles — Pasadena (510)": 510,
    "Grand Los Angeles — Santa Monica (548)": 548,
    "Grand Los Angeles — Torrance (592)": 592,
    "Grand Los Angeles — West Covina (591)": 591,
    "Orange County / Sud — Costa Mesa (627)": 627,
    "Orange County / Sud — Fullerton (547)": 547,
    "Orange County / Sud — Laguna Hills (642)": 642,
    "Orange County / Sud — Santa Ana (529)": 529,
    "Orange County / Sud — San Clemente (652)": 652,
    "Orange County / Sud — Westminster (623)": 623,
    "San Diego & Environs — Chula Vista (609)": 609,
    "San Diego & Environs — El Cajon (549)": 549,
    "San Diego & Environs — Oceanside (593)": 593,
    "San Diego & Environs — San Diego (Clairemont) (618)": 618,
    "San Diego & Environs — San Diego (Normal St) (504)": 504,
    "San Diego & Environs — San Marcos (637)": 637,
    "San Diego & Environs — San Ysidro (649)": 649,
    "Sacramento / Nord — Auburn (533)": 533,
    "Sacramento / Nord — Chico (534)": 534,
    "Sacramento / Nord — Eureka (522)": 522,
    "Sacramento / Nord — Redding (550)": 550,
    "Sacramento / Nord — Roseville (635)": 635,
    "Sacramento / Nord — Sacramento (Broadway) (500)": 500,
    "Sacramento / Nord — Sacramento (South) (603)": 603,
    "Sacramento / Nord — Woodland (535)": 535,
    "Vallée Centrale — Bakersfield (511)": 511,
    "Vallée Centrale — Fresno (505)": 505,
    "Vallée Centrale — Lodi (595)": 595,
    "Vallée Centrale — Modesto (536)": 536,
    "Vallée Centrale — Stockton (517)": 517,
    "Vallée Centrale — Visalia (519)": 519
}

# ==========================
# Module d'analyse AAMVA / PF417
# ==========================
def analyseur_permis_californie(donnees_brutes):
    champs_aamva = {
        "DAQ": "Numéro de Permis",
        "DCS": "Nom de Famille",
        "DCT": "Prénom",
        "DAG": "Adresse complète",
        "DAI": "Ville",
        "DAJ": "État",
        "DAK": "Code Postal",
        "DBB": "Date de Naissance (DOB)",
        "DBA": "Date d'Expiration (EXP)",
        "DBD": "Date d'Émission (ISS)",
        "DBC": "Sexe",
        "DAU": "Taille (inches)",
        "DAY": "Yeux",
        "DAZ": "Cheveux",
        "DAW": "Poids (lb)"
    }

    resultats = {}
    maintenant = dt.now()

    for code, label in champs_aamva.items():
        pattern = f"{code}(.*?)(?=[D][A-Z][A-Z]|$)"
        match = re.search(pattern, donnees_brutes)
        resultats[label] = match.group(1).strip() if match else "NON_DETECTE"

    # Validation EXP
    date_exp_str = resultats.get("Date d'Expiration (EXP)","")
    try:
        date_exp_obj = dt.strptime(date_exp_str, "%m%d%Y")
        resultats["STATUT_VALIDITE"] = "🟢 VALIDE" if date_exp_obj >= maintenant else f"🔴 EXPIRE ({date_exp_obj.strftime('%d/%m/%Y')})"
    except:
        resultats["STATUT_VALIDITE"] = "⚠️ ERREUR_FORMAT_DATE"

    # DOB
    dob_str = resultats.get("Date de Naissance (DOB)","")
    try:
        dob_obj = dt.strptime(dob_str, "%m%d%Y")
        resultats["DOB_FORMAT"] = dob_obj.strftime("%d/%m/%Y")
    except:
        resultats["DOB_FORMAT"] = "⚠️ ERREUR_FORMAT_DATE"

    # ISS
    iss_str = resultats.get("Date d'Émission (ISS)","")
    try:
        iss_obj = dt.strptime(iss_str, "%m%d%Y")
        resultats["ISS_FORMAT"] = iss_obj.strftime("%d/%m/%Y")
    except:
        resultats["ISS_FORMAT"] = "⚠️ ERREUR_FORMAT_DATE"

    # Vérification DL Californien
    num_dl = resultats.get("Numéro de Permis","")
    resultats["VERIFICATION_DL"] = "✅ Format Californien Conforme" if re.match(r"^[A-Z][0-9]{7}$", num_dl) else "❌ Format Invalide"

    return resultats

# ==========================
# Formulaire Streamlit
# ==========================
st.title("Générateur officiel de permis CA")

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
office_choice = st.selectbox("Field Office", list(offices.keys()))
generate = st.button("Générer la carte")

# ==========================
# GÉNÉRATION DE LA CARTE
# ==========================
if generate:
    r = random.Random(seed(ln,fn,dob))
    dl = rletter(r, ln[0]) + rdigits(r,7)
    exp_year = iss.year + 5
    exp = datetime.date(exp_year, dob.month, dob.day)
    office_code = offices[office_choice]
    seq = next_sequence(r)
    dd = f"{iss.strftime('%m/%d/%Y')}{office_code}{seq}FD/{iss.year%100}"

    # Création du code PF417 simulé pour test
    raw_input_pf417 = (
        f"DAQ{dl}DCS{ln}DCT{fn}DAG123 MAIN STDAIANYDAJCA"
        f"DAK12345DBB{dob.strftime('%m%d%Y')}DBA{exp.strftime('%m%d%Y')}DBD{iss.strftime('%m%d%Y')}"
        f"DBCFDAU{h1*12+h2}DAY{eyes}DAZ{hair}DAW{w}"
    )
    analyse = analyseur_permis_californie(raw_input_pf417)

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
                <div class="label">ISS</div>
                <div class="value">{iss.strftime('%m/%d/%Y')}</div>
                <div class="label">EXP</div>
                <div class="value">{exp.strftime('%m/%d/%Y')}</div>
                <div class="label">Classe</div>
                <div class="value">{cls}</div>
                <div class="label">Restrictions</div>
                <div class="value">{rstr}</div>
                <div class="label">Endorsements</div>
                <div class="value">{endorse}</div>
                <div class="label">Yeux / Cheveux / Taille / Poids</div>
                <div class="value">{eyes} / {hair} / {h1}'{h2}'' / {w} lb</div>
                <div class="label">STATUT VALIDITÉ / Vérification DL</div>
                <div class="value">{analyse['STATUT_VALIDITE']} / {analyse['VERIFICATION_DL']}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
