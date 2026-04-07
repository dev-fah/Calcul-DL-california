# driver_licence_uiux_grid.py
# Générateur DL avec interface UI/UX en colonnes et cartes
# Dépendances : streamlit, pandas, openpyxl
# pip install streamlit pandas openpyxl

import streamlit as st
import pandas as pd
import datetime
import hashlib
import random
import json
from io import BytesIO

st.set_page_config(page_title="Générateur DL Officiel", layout="wide")

# -------------------------
# CSS pour UI/UX moderne
# -------------------------
st.markdown("""
<style>
body { background: #f9fafb; font-family: 'Segoe UI', sans-serif; }
h1, h2, h3 { font-weight: 700; color: #1e293b; }
.card {
    background:#fff; border-radius:12px; padding:20px;
    box-shadow:0 6px 18px rgba(0,0,0,0.06); margin-bottom:20px;
}
.stButton>button {
    background: linear-gradient(90deg,#2563eb,#7c3aed);
    color:white; border-radius:10px; padding:10px 20px;
    font-weight:600; box-shadow:0 6px 14px rgba(37,99,235,0.12);
}
.stDownloadButton>button {
    background: linear-gradient(90deg,#06b6d4,#0ea5e9);
    color:white; border-radius:10px; padding:10px 20px;
    font-weight:600; box-shadow:0 6px 14px rgba(6,182,212,0.12);
}
div[data-baseweb="select"] span { font-weight:bold !important; }
</style>
""", unsafe_allow_html=True)

# -------------------------
# Utilitaires
# -------------------------
def deterministic_seed(*parts: str) -> int:
    key = "|".join([p or "" for p in parts])
    return int(hashlib.md5(key.encode("utf-8")).hexdigest()[:8], 16)

def random_digits(rnd: random.Random, length: int) -> str:
    return "".join(rnd.choice("0123456789") for _ in range(length))

def random_letter(rnd: random.Random) -> str:
    return rnd.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def format_date_us(d: datetime.date) -> str:
    return d.strftime("%m/%d/%Y")

def format_height(feet: int, inches: int) -> str:
    return f"{feet}'-{inches:02d}\""

def to_json_bytes(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")

def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

def to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Résultats")
    return buf.getvalue()

# -------------------------
# Interface principale
# -------------------------
st.title("🆔 Générateur DL et DD (UI/UX en colonnes)")
st.caption("Interface compacte et moderne — champs organisés côte à côte.")

with st.form(key="form_main"):
    # Carte infos personnelles
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("👤 Informations personnelles")
    col1, col2, col3 = st.columns(3)
    with col1: ln = st.text_input("Nom de famille (LN)", value="HARMS")
    with col2: fn = st.text_input("Prénom (FN)", value="ROSA")
    with col3: sex = st.selectbox("Sexe (SEX)", ["M", "F", "X"], index=1)
    dob = st.date_input("Date de naissance (DOB)", value=datetime.date(1995, 3, 15))
    st.markdown("</div>", unsafe_allow_html=True)

    # Carte caractéristiques physiques
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📏 Caractéristiques physiques")
    col4, col5, col6 = st.columns(3)
    with col4: hgt_feet = st.number_input("Taille - pieds", min_value=0, max_value=8, value=5)
    with col5: hgt_inches = st.number_input("Taille - pouces", min_value=0, max_value=11, value=10)
    with col6: wgt = st.number_input("Poids (lbs)", min_value=50, max_value=400, value=160)
    col7, col8 = st.columns(2)
    with col7: hair = st.text_input("Cheveux (HAIR, 3 lettres)", value="BRN")
    with col8: eyes = st.text_input("Yeux (EYES, 3 lettres)", value="BLU")
    st.markdown("</div>", unsafe_allow_html=True)

    # Carte détails administratifs
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📑 Détails administratifs")
    col9, col10 = st.columns(2)
    with col9: iss = st.date_input("Date d’émission (ISS)", value=datetime.date(2024, 6, 10))
    with col10: fo = st.selectbox("Bureau (Field Office)", [
        "San Jose (654) - Silicon Valley",
        "Fresno (210) - Central Valley",
        "Oakland (987) - East Bay",
        "Riverside (543) - Inland Empire",
        "Santa Ana (876) - Orange County",
        "Bakersfield (102) - Central Valley",
        "Long Beach (304) - Greater Los Angeles Area",
        "San Bernardino (607) - Inland Empire",
        "Stockton (412) - Central Valley",
        "Santa Barbara (205) - Central Coast",
        "Redding (530) - Far Northern California",
        "Eureka (707) - North Coast"
    ])
    col11, col12, col13 = st.columns(3)
    with col11: class_ = st.text_input("Classe (CLASS)", value="C")
    with col12: rstr = st.text_input("Restrictions (RSTR)", value="NONE")
    with col13: end = st.text_input("Endorsements (END)", value="")
    st.markdown("</div>", unsafe_allow_html=True)

    export_format = st.selectbox("Format d'export", ["JSON", "CSV", "XLSX"])
    calculate = st.form_submit_button("⚙️ Calculer")

# -------------------------
# Traitement
# -------------------------
if calculate:
    rnd = random.Random(deterministic_seed(ln, fn, dob.isoformat()))
    dl_number = random_letter(rnd) + random_digits(rnd, 7)
    exp_date = iss.replace(year=iss.year + 6)
    dob_str, iss_str, exp_str = format_date_us(dob), format_date_us(iss), format_date_us(exp_date)
    ln, fn = ln.upper(), fn.upper()
    hair, eyes = hair.upper()[:3].ljust(3, "X"), eyes.upper()[:3].ljust(3, "X")
    hgt = format_height(int(hgt_feet), int(hgt_inches))
    dd = f"{iss_str.replace('/','')}{random_digits(rnd,6)}"

    result = {
        "DL_NUMBER": dl_number, "LN": ln, "FN": fn, "SEX": sex,
        "DOB": dob_str, "HGT": hgt, "WGT": f"{wgt} lb",
        "HAIR": hair, "EYES": eyes, "ISS": iss_str, "EXP": exp_str,
        "CLASS": class_, "RSTR": rstr, "END": end, "FO": fo,
        "DD": dd, "GENERATED_AT": datetime.datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S")
    }

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📊 Aperçu officiel")
    st.json(result)
    st.markdown("</div>", unsafe_allow_html=True)

    if export_format == "JSON":
        data_bytes, mime, fname = to_json_bytes(result), "application/json", "dl_officiel.json"
    elif export_format == "CSV":
        data_bytes, mime, fname = to_csv_bytes(pd.DataFrame([result])), "textTu as raison : pour que ton interface ressemble à la maquette moderne que tu m’as montrée (style **SIGN UP**), il faut **organiser les champs en colonnes et cartes**, plutôt que de les empiler avec de grandes lignes horizontales. Cela donne une interface compacte, élégante et professionnelle.

---

### 🎨 Principes appliqués
- **Cartes visuelles** : chaque section (infos perso, physiques, administratives) est dans une carte avec ombre et arrondis.  
- **Colonnes côte à côte** : les champs sont alignés en 2 ou 3 colonnes pour gagner de la place.  
- **Boutons stylisés** : arrondis, dégradés, avec icônes.  
- **Menu déroulant Field Office** : stylisé en gras via CSS.  
- **Feedback clair** : résultats affichés dans une carte JSON bien séparée.

---

### 📝 Code complet (version finale UI/UX en colonnes)

```python
# driver_licence_uiux_grid_final.py
# Générateur DL avec interface UI/UX moderne en colonnes
# Dépendances : streamlit, pandas, openpyxl
# pip install streamlit pandas openpyxl

import streamlit as st
import pandas as pd
import datetime
import hashlib
import random
import json
from io import BytesIO

st.set_page_config(page_title="Générateur DL Officiel", layout="wide")

# -------------------------
# CSS pour UI/UX moderne
# -------------------------
st.markdown("""
<style>
body { background: #f9fafb; font-family: 'Segoe UI', sans-serif; }
h1, h2, h3 { font-weight: 700; color: #1e293b; }
.card {
    background:#fff; border-radius:12px; padding:20px;
    box-shadow:0 6px 18px rgba(0,0,0,0.06); margin-bottom:20px;
}
.stButton>button {
    background: linear-gradient(90deg,#2563eb,#7c3aed);
    color:white; border-radius:10px; padding:10px 20px;
    font-weight:600; box-shadow:0 6px 14px rgba(37,99,235,0.12);
}
.stDownloadButton>button {
    background: linear-gradient(90deg,#06b6d4,#0ea5e9);
    color:white; border-radius:10px; padding:10px 20px;
    font-weight:600; box-shadow:0 6px 14px rgba(6,182,212,0.12);
}
div[data-baseweb="select"] span { font-weight:bold !important; }
</style>
""", unsafe_allow_html=True)

# -------------------------
# Utilitaires
# -------------------------
def deterministic_seed(*parts: str) -> int:
    key = "|".join([p or "" for p in parts])
    return int(hashlib.md5(key.encode("utf-8")).hexdigest()[:8], 16)

def random_digits(rnd: random.Random, length: int) -> str:
    return "".join(rnd.choice("0123456789") for _ in range(length))

def random_letter(rnd: random.Random) -> str:
    return rnd.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def format_date_us(d: datetime.date) -> str:
    return d.strftime("%m/%d/%Y")

def format_height(feet: int, inches: int) -> str:
    return f"{feet}'-{inches:02d}\""

def to_json_bytes(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")

def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

def to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Résultats")
    return buf.getvalue()

# -------------------------
# Interface principale
# -------------------------
st.title("🆔 Générateur DL et DD (UI/UX en colonnes)")
st.caption("Interface compacte et moderne — champs organisés côte à côte.")

with st.form(key="form_main"):
    # Carte infos personnelles
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("👤 Informations personnelles")
    col1, col2, col3 = st.columns(3)
    with col1: ln = st.text_input("Nom de famille (LN)", value="HARMS")
    with col2: fn = st.text_input("Prénom (FN)", value="ROSA")
    with col3: sex = st.selectbox("Sexe (SEX)", ["M", "F", "X"], index=1)
    dob = st.date_input("Date de naissance (DOB)", value=datetime.date(1995, 3, 15))
    st.markdown("</div>", unsafe_allow_html=True)

    # Carte caractéristiques physiques
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📏 Caractéristiques physiques")
    col4, col5, col6 = st.columns(3)
    with col4: hgt_feet = st.number_input("Taille - pieds", min_value=0, max_value=8, value=5)
    with col5: hgt_inches = st.number_input("Taille - pouces", min_value=0, max_value=11, value=10)
    with col6: wgt = st.number_input("Poids (lbs)", min_value=50, max_value=400, value=160)
    col7, col8 = st.columns(2)
    with col7: hair = st.text_input("Cheveux (HAIR, 3 lettres)", value="BRN")
    with col8: eyes = st.text_input("Yeux (EYES, 3 lettres)", value="BLU")
    st.markdown("</div>", unsafe_allow_html=True)

    # Carte détails administratifs
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📑 Détails administratifs")
    col9, col10 = st.columns(2)
    with col9: iss = st.date_input("Date d’émission (ISS)", value=datetime.date(2024, 6, 10))
    with col10: fo = st.selectbox("Bureau (Field Office)", [
        "San Jose (654) - Silicon Valley",
        "Fresno (210) - Central Valley",
        "Oakland (987) - East Bay",
        "Riverside (543) - Inland Empire",
        "Santa Ana (876) - Orange County",
        "Bakersfield (102) - Central Valley",
        "Long Beach (304) - Greater Los Angeles Area",
        "San Bernardino (607) - Inland Empire",
        "Stockton (412) - Central Valley",
        "Santa Barbara (205) - Central Coast",
        "Redding (530) - Far Northern California",
        "Eureka (707) - North Coast"
    ])
    col11, col12, col13 = st.columns(3)
    with col11: class_ = st.text_input("Classe (CLASS)", value="C")
    with col12: rstr = st.text_input("Restrictions (RSTR)", value="NONE")
    with col13: end = st.text_input("Endorsements (END)", value="")
    st.markdown("</div>", unsafe_allow_html=True)

    export_format = st.selectbox("Format d'export", ["JSON", "CSV", "XLSX"])
    calculate = st.form_submit_button("⚙️ Calculer")

# -------------------------
# Traitement
# -------------------------
if calculate:
    rnd = random.Random(deterministic_seed(ln, fn, dob.isoformat()))
    dl_number = random_letter(rnd) + random_digits(rnd, 7)
    exp_date = iss.replace(year=iss.year + 6)
    dob_str, iss_str, exp_str = format_date_us(dob), format_date_us(iss), format_date_us(exp_date)
    ln, fn = ln.upper(), fn.upper()
    hair, eyes = hair.upper()[:3].ljust(3, "X"), eyes.upper()[:3].ljust(3, "X")
    hgt = format_height(int(hgt_feet), int(hgt_inches))
    dd = f"{iss_str.replace('/','')}{random_digits(rnd,6)}"

    result = {
        "DL_NUMBER": dl_number, "LN": ln, "FN": fn, "SEX": sex,
        "DOB": dob_str, "HGT": hgt, "WGT": f"{wgt} lb",
        "HAIR": hair, "EYES": eyes, "ISS": iss_str, "EXP": exp_str,
        "CLASS": class_, "RSTR": rstr, "END": end, "FO": fo,
        "DD": dd, "GENERATED_AT": datetime.datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S")
    }

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📊 Aperçu officiel")
    st.json(result)
    st.markdown("</div>", unsafe_allow_html=True)

    if export_format == "JSON":
        data_bytes, mime, fname = to_json_bytes(result), "application/json", "dl_officiel.json"
    elif export_format == "CSV":
        data_bytes, mime
