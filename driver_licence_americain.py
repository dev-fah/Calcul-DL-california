# driver_license_final_full_visible.py

import streamlit as st
import datetime, random, hashlib, re
from datetime import datetime as dt

st.set_page_config(page_title="Permis CA", layout="centered")

# ==========================
# CSS
# ==========================
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
    font-weight:700;
    font-size:14px;
}
.body { display:flex; gap:12px; }
.photo {
    width:90px; height:110px;
    background:#e5e7eb; border-radius:8px;
}
.label { opacity:0.7; font-size:10px; }
.value { font-weight:700; margin-bottom:4px; }

.analysis {
    margin-top:20px;
    padding:12px;
    border-radius:10px;
    background:#f8fafc;
    border:1px solid #e5e7eb;
}
</style>
""", unsafe_allow_html=True)

# ==========================
# Utils
# ==========================
def seed(*x):
    return int(hashlib.md5("|".join(map(str,x)).encode()).hexdigest()[:8],16)

def rdigits(r,n):
    return "".join(r.choice("0123456789") for _ in range(n))

def rletter(r, initial):
    return initial.upper()

def next_sequence(r):
    return str(r.randint(10,99))

# ==========================
# Offices (complet)
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
# Analyse PF417
# ==========================
def analyseur(data):
    res = {}

    def find(code):
        m = re.search(f"{code}(.*?)(?=[D][A-Z][A-Z]|$)", data)
        return m.group(1).strip() if m else "?"

    res["DL"] = find("DAQ")
    res["Nom"] = find("DCS")
    res["Prenom"] = find("DCT")
    res["DOB"] = find("DBB")
    res["EXP"] = find("DBA")

    # validation DL
    res["DL_OK"] = "✅" if re.match(r"^[A-Z][0-9]{7}$", res["DL"]) else "❌"

    return res

# ==========================
# FORMULAIRE
# ==========================
st.title("Permis Californie")

ln = st.text_input("Nom", "HARMS")
fn = st.text_input("Prénom", "ROSA")
sex = st.selectbox("Sexe", ["M","F"])
dob = st.date_input("DOB", datetime.date(1990,1,1))
iss = st.date_input("ISS", datetime.date.today())
office_choice = st.selectbox("Field Office", list(offices.keys()))

generate = st.button("Générer")

# ==========================
# RESULTAT
# ==========================
if generate:

    r = random.Random(seed(ln,fn,dob))
    dl = rletter(r, ln[0]) + rdigits(r,7)

    exp = datetime.date(iss.year+5, dob.month, dob.day)

    office_code = offices[office_choice]
    seq = next_sequence(r)

    dd = f"{iss.strftime('%m/%d/%Y')}{office_code}{seq}FD/{iss.year%100}"

    raw = f"DAQ{dl}DCS{ln}DCT{fn}DBB{dob.strftime('%m%d%Y')}DBA{exp.strftime('%m%d%Y')}"
    analyse = analyseur(raw)

    # CARTE
    st.markdown(f"""
    <div class="card">
        <div class="header">
            <div>CALIFORNIA DRIVER LICENSE</div>
            <div>{dl}</div>
        </div>

        <div class="body">
            <div class="photo"></div>
            <div>
                <div class="label">Nom</div>
                <div class="value">{ln}</div>

                <div class="label">Prénom</div>
                <div class="value">{fn}</div>

                <div class="label">DOB</div>
                <div class="value">{dob.strftime('%m/%d/%Y')}</div>

                <div class="label">ISS / EXP</div>
                <div class="value">{iss.strftime('%m/%d/%Y')} / {exp.strftime('%m/%d/%Y')}</div>

                <div class="label">DD</div>
                <div class="value">{dd}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ANALYSE VISIBLE
    st.markdown("<div class='analysis'>", unsafe_allow_html=True)
    st.subheader("Analyse Code Barre (PF417)")
    st.write(analyse)
    st.markdown("</div>", unsafe_allow_html=True)
