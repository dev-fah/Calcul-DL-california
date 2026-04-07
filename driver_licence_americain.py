# driver_licence_uiux_aligned_fix.py
# Aperçu visuel avec sections Sexe et Yeux/Cheveux correctement alignées
# Dépendances : streamlit, pandas
# Installation : pip install streamlit pandas

import streamlit as st
import datetime
import hashlib
import random
import json
from io import BytesIO
import pandas as pd

st.set_page_config(page_title="Aperçu Permis - Aligné Fix", layout="wide")

# CSS pour alignement précis et colonnes fixes
st.markdown("""
<style>
:root{
  --bg: #f6f8fb;
  --card: #ffffff;
  --accent: #2563eb;
  --muted: #6b7280;
  --shadow: 0 10px 30px rgba(2,6,23,0.08);
}
body { background: var(--bg); font-family: "Segoe UI", Roboto, Arial, sans-serif; color:#0f172a; }
.card { background: var(--card); border-radius:12px; padding:18px; box-shadow: var(--shadow); margin-bottom:18px; }
.dl-wrapper { display:flex; gap:18px; align-items:flex-start; }
.dl-left { width:34%; min-width:220px; border-radius:10px; padding:14px; background: linear-gradient(135deg, rgba(37,99,235,0.04), rgba(124,58,237,0.02)); }
.mini-graphic { width:100%; height:120px; border-radius:8px; background: linear-gradient(90deg,#e6eefc,#f3eefe); display:flex; align-items:center; justify-content:center; color:var(--muted); font-weight:700; }
.dl-right { flex:1; display:flex; flex-direction:column; gap:12px; }
.row { display:flex; gap:12px; align-items:center; }
.col { display:flex; flex-direction:column; gap:4px; }
.label { font-size:12px; color:var(--muted); }
.value { font-size:16px; color:#0f172a; font-weight:800; }
.sub { font-size:13px; color:var(--muted); }
.right-block { display:flex; flex-direction:column; align-items:flex-start; gap:4px; min-width:220px; } /* left-align inside right block */
.right-block .label { text-align:left; }
.right-block .value { text-align:left; }
.grid-2 { display:grid; grid-template-columns: 1fr 1fr; gap:12px; }
.meta { font-size:12px; color:var(--muted); margin-top:8px; }
.badge { background: linear-gradient(90deg,var(--accent),#7c3aed); color:white; padding:6px 10px; border-radius:999px; font-weight:800; }
@media (max-width:880px) {
  .dl-wrapper { flex-direction:column; }
  .right-block { align-items:flex-start; text-align:left; min-width:auto; }
}
</style>
""", unsafe_allow_html=True)

# Utilitaires
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

# Formulaire
st.title("Générateur Permis — Alignement corrigé")
st.caption("Modifie les champs puis clique sur Générer. Les sections sont alignées à gauche dans la colonne droite.")

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

# Rendu aligné (corrigé)
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
        "DL_NUMBER": dl_number,
        "LN": ln_u,
        "FN": fn_u,
        "SEX": sex,
        "DOB": dob_str,
        "HGT": hgt,
        "WGT": f"{wgt} lb",
        "HAIR": hair_u,
        "EYES": eyes_u,
        "ISS": iss_str,
        "EXP": exp_str,
        "CLASS": class_,
        "RSTR": rstr,
        "END": end,
        "FO": fo,
        "DD": dd,
        "GENERATED_AT": generated_at
    }

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;'>"
                f"<div><h3 style='margin:0'>Aperçu officiel</h3><div class='sub' style='margin-top:4px'>Sections alignées à gauche</div></div>"
                f"<div class='badge'>DL #{dl_number}</div>"
                "</div>", unsafe_allow_html=True)

    cols = st.columns([0.34, 0.66])
    with cols[0]:
        st.markdown("<div class='dl-left'>", unsafe_allow_html=True)
        st.markdown("<div class='mini-graphic'>APERÇU VISUEL</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown("<div class='label'>Bureau</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='value'>{result['FO']}</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown("<div class='label'>Document ID</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='sub'>{result['DD']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with cols[1]:
        st.markdown("<div class='dl-right'>", unsafe_allow_html=True)

        # Nom à gauche, bloc d'information (Sexe + DOB) à GAUCHE-ALIGNED dans la colonne droite
        st.markdown("<div class='row'>", unsafe_allow_html=True)
        left_col, info_block = st.columns([0.7, 0.3])
        with left_col:
            st.markdown("<div class='col'>", unsafe_allow_html=True)
            st.markdown("<div class='label'>Nom</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='value'>{result['LN']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='sub'>Prénom: {result['FN']}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with info_block:
            # **Important** : left-align the info block content (not right-aligned)
            st.markdown("<div class='right-block'>", unsafe_allow_html=True)
            st.markdown("<div class='label'>Sexe</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='value'>{result['SEX']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='sub'>Né(e): {result['DOB']}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Taille / Poids on left, Yeux/Cheveux + Classe on right — both left-aligned inside their columns
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        left2, right2 = st.columns([0.6, 0.4])
        with left2:
            st.markdown("<div class='label'>Taille</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='value'>{result['HGT']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='sub'>Poids: {result['WGT']}</div>", unsafe_allow_html=True)
        with right2:
            st.markdown("<div class='right-block'>", unsafe_allow_html=True)
            st.markdown("<div class='label'>Yeux / Cheveux</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='value'>{result['EYES']} / {result['HAIR']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='sub'>Classe: {result['CLASS']}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Dates
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        dcols = st.columns(2)
        with dcols[0]:
            st.markdown("<div class='label'>Date d'émission</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='value'>{result['ISS']}</div>", unsafe_allow_html=True)
        with dcols[1]:
            st.markdown("<div class='label'>Date d'expiration</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='value'>{result['EXP']}</div>", unsafe_allow_html=True)

        st.markdown(f"<div class='meta'>Généré le: {result['GENERATED_AT']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.success("✅ Alignement rectifié — les sections sont maintenant left‑aligned dans la colonne droite.")
