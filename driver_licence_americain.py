# driver_licence_uiux_three_columns.py
# Aperçu UI/UX divisé en trois sections (gauche, centre, droite)
# Dépendances : streamlit, pandas
# Installation : pip install streamlit pandas

import streamlit as st
import datetime
import hashlib
import random
import json
from io import BytesIO
import pandas as pd

st.set_page_config(page_title="Aperçu Permis - 3 Sections", layout="wide")

# -------------------------
# CSS pour 3 sections et alignement (Sexe = référence)
# -------------------------
st.markdown("""
<style>
:root{
  --bg:#f6f8fb; --card:#ffffff; --accent:#2563eb; --muted:#6b7280; --shadow:0 10px 30px rgba(2,6,23,0.08);
}
body { background:var(--bg); font-family: "Segoe UI", Roboto, Arial, sans-serif; color:#0f172a; }
.container { padding:18px; }
.card { background:var(--card); border-radius:12px; padding:18px; box-shadow:var(--shadow); margin-bottom:18px; }
.three-cols { display:flex; gap:18px; align-items:flex-start; }
.col-left { width:28%; min-width:220px; border-radius:10px; padding:14px; background: linear-gradient(135deg, rgba(37,99,235,0.04), rgba(124,58,237,0.02)); }
.col-center { width:36%; min-width:300px; border-radius:10px; padding:14px; background:transparent; }
.col-right { flex:1; border-radius:10px; padding:14px; background:transparent; }

/* Grille interne : la colonne de référence (Sexe) a une largeur fixe */
.info-grid {
  display:grid;
  grid-template-columns: 140px 1fr; /* 140px = référence (Sexe) */
  gap:8px 18px;
  align-items:start;
}
.ref-col { display:flex; flex-direction:column; align-items:flex-start; }
.right-col { display:flex; flex-direction:column; gap:8px; }

/* Styles texte */
.label { font-size:12px; color:var(--muted); }
.value { font-size:16px; color:#0f172a; font-weight:800; }
.sub { font-size:13px; color:var(--muted); }
.badge { background: linear-gradient(90deg,var(--accent),#7c3aed); color:white; padding:6px 10px; border-radius:999px; font-weight:800; }

/* Responsive */
@media (max-width:980px) {
  .three-cols { flex-direction:column; }
  .info-grid { grid-template-columns: 1fr; }
}
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

# -------------------------
# Formulaire
# -------------------------
st.title("Générateur Permis — 3 Sections")
st.caption("Les trois sections : gauche = identification, centre = identité, droite = caractéristiques et dates.")

with st.form(key="form_main"):
    c1, c2, c3 = st.columns([1.2, 1.2, 0.8])
    with c1:
        ln = st.text_input("Nom de famille (LN)", value="HARMS")
        dob = st.date_input("Date de naissance (DOB)", value=datetime.date(1995, 3, 15))
    with c2:
        fn = st.text_input("Prénom (FN)", value="ROSA")
        sex = st.selectbox("Sexe (SEX)", ["M", "F", "X"], index=1)
    with c3:
        st.write("")
        st.write("")
        st.write("")

    c4, c5, c6 = st.columns(3)
    with c4:
        hgt_feet = st.number_input("Taille - pieds", min_value=0, max_value=8, value=5)
    with c5:
        hgt_inches = st.number_input("Taille - pouces", min_value=0, max_value=11, value=10)
    with c6:
        wgt = st.number_input("Poids (lbs)", min_value=50, max_value=400, value=160)

    c7, c8 = st.columns(2)
    with c7:
        hair = st.text_input("Cheveux (HAIR, 3 lettres)", value="BRN")
    with c8:
        eyes = st.text_input("Yeux (EYES, 3 lettres)", value="BLU")

    c9, c10 = st.columns(2)
    with c9:
        iss = st.date_input("Date d’émission (ISS)", value=datetime.date(2024, 6, 10))
    with c10:
        fo = st.selectbox("Bureau (Field Office)", [
            "San Jose (654) - Silicon Valley",
            "Fresno (210) - Central Valley",
            "Oakland (987) - East Bay",
            "Riverside (543) - Inland Empire",
            "Santa Ana (876) - Orange County"
        ])

    c11, c12, c13 = st.columns(3)
    with c11:
        class_ = st.text_input("Classe (CLASS)", value="C")
    with c12:
        rstr = st.text_input("Restrictions (RSTR)", value="NONE")
    with c13:
        end = st.text_input("Endorsements (END)", value="")

    submit = st.form_submit_button("⚙️ Générer l'aperçu")

# -------------------------
# Rendu 3 sections
# -------------------------
if submit:
    rnd = random.Random(deterministic_seed(ln, fn, dob.isoformat()))
    dl_number = random_letter(rnd) + random_digits(rnd, 7)
    exp_date = iss.replace(year=iss.year + 6)
    dob_str = format_date_us(dob)
    iss_str = format_date_us(iss)
    exp_str = format_date_us(exp_date)
    ln_u, fn_u = ln.upper(), fn.upper()
    hair_u = hair.upper()[:3].ljust(3, "X")
    eyes_u = eyes.upper()[:3].ljust(3, "X")
    hgt = format_height(int(hgt_feet), int(hgt_inches))
    dd = f"{iss_str.replace('/','')}{random_digits(rnd,6)}"
    generated_at = datetime.datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S")

    result = {
        "DL_NUMBER": dl_number, "LN": ln_u, "FN": fn_u, "SEX": sex, "DOB": dob_str,
        "HGT": hgt, "WGT": f"{wgt} lb", "HAIR": hair_u, "EYES": eyes_u,
        "ISS": iss_str, "EXP": exp_str, "CLASS": class_, "FO": fo, "DD": dd,
        "GENERATED_AT": generated_at
    }

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;'>"
                f"<div><h3 style='margin:0'>Aperçu officiel</h3><div class='sub' style='margin-top:4px'>Disposition en trois sections</div></div>"
                f"<div class='badge'>DL #{dl_number}</div></div>", unsafe_allow_html=True)

    # Trois sections côte à côte
    st.markdown("<div class='three-cols'>", unsafe_allow_html=True)

    # Section gauche : identification / mini-illustration
    st.markdown("<div class='col-left'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>IDENTIFICATION</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.markdown("<div style='background:linear-gradient(90deg,#e6eefc,#f3eefe); height:120px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-weight:700; color:var(--muted)'>APERÇU VISUEL</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Bureau</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='value'>{result['FO']}</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Document ID</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>{result['DD']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Section centre : identité (Nom, Prénom, Sexe référence)
    st.markdown("<div class='col-center'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Nom</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='value'>{result['LN']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>Prénom: {result['FN']}</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Grille interne alignée sur la colonne de référence (Sexe)
    st.markdown("<div class='info-grid'>", unsafe_allow_html=True)

    # Colonne de référence (Sexe)
    st.markdown("<div class='ref-col'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Sexe</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='value'>{result['SEX']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>Né(e): {result['DOB']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Contenu à droite de la référence (espace pour aligner)
    st.markdown("<div class='right-col'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Taille</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='value'>{result['HGT']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>Poids: {result['WGT']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Yeux / Cheveux ligne (référence vide + contenu)
    st.markdown("<div class='ref-col'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>&nbsp;</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='right-col'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Yeux / Cheveux</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='value'>{result['EYES']} / {result['HAIR']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>Classe: {result['CLASS']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Dates (span across both columns)
    st.markdown("<div style='grid-column: 1 / -1; display:flex; gap:18px; margin-top:8px;'>", unsafe_allow_html=True)
    st.markdown("<div style='flex:1'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Date d'émission</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='value'>{result['ISS']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='flex:1'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Date d'expiration</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='value'>{result['EXP']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # close info-grid
    st.markdown("</div>", unsafe_allow_html=True)  # close col-center

    # Section droite : informations complémentaires / métadonnées
    st.markdown("<div class='col-right'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Numéro de permis</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='value'>{result['DL_NUMBER']}</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Restrictions</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>{result['RSTR']}</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Endorsements</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>{result['END']}</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>Généré le: {result['GENERATED_AT']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # close three-cols
    st.markdown("</div>", unsafe_allow_html=True)  # close card

    st.success("✅ Disposition en trois sections appliquée. Les champs restent modifiables depuis le formulaire.")
