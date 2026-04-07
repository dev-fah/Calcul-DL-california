# driver_licence_uiux_clean.py
# Aperçu UI/UX propre — aucun code HTML affiché publiquement
# Dépendances : streamlit, pandas
# Installation : pip install streamlit pandas

import streamlit as st
import pandas as pd
import datetime
import hashlib
import random

st.set_page_config(page_title="Aperçu Permis - UI/UX", layout="wide")

# -------------------------
# CSS léger pour l'aperçu
# -------------------------
st.markdown(
    """
    <style>
    :root {
      --bg: #f6f8fb;
      --card: #ffffff;
      --accent: #2563eb;
      --muted: #6b7280;
      --shadow: 0 8px 24px rgba(15,23,42,0.06);
    }
    .page { background: var(--bg); padding: 18px 24px; }
    .card { background: var(--card); border-radius:12px; padding:18px; box-shadow: var(--shadow); }
    .dl-card { display:flex; gap:18px; align-items:flex-start; }
    .dl-left { width:36%; min-width:220px; background: linear-gradient(135deg, rgba(37,99,235,0.04), rgba(124,58,237,0.02)); padding:14px; border-radius:10px; }
    .dl-photo { width:100%; height:160px; background:linear-gradient(90deg,#e6eefc,#f3eefe); border-radius:8px; display:flex; align-items:center; justify-content:center; color:var(--muted); font-weight:700; }
    .dl-meta { margin-top:12px; font-size:13px; color:#0f172a; font-weight:600; }
    .dl-right { flex:1; display:flex; flex-direction:column; gap:10px; }
    .row { display:flex; justify-content:space-between; gap:12px; align-items:center; }
    .label { font-size:12px; color:var(--muted); }
    .value { font-size:16px; color:#0f172a; font-weight:700; }
    .sub { font-size:13px; color:var(--muted); }
    .badge { background: linear-gradient(90deg,#2563eb,#7c3aed); color:white; padding:6px 10px; border-radius:999px; font-weight:700; }
    @media (max-width:880px) {
      .dl-card { flex-direction:column; }
      .dl-left { width:100%; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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
# Formulaire (entrée)
# -------------------------
st.title("Générateur Permis — Aperçu UI/UX")
st.caption("Remplis les champs puis clique sur Générer pour voir l'aperçu visuel (aucun code source affiché).")

with st.form("form"):
    col1, col2, col3 = st.columns([1.2, 1.2, 0.8])
    with col1:
        ln = st.text_input("Nom de famille (LN)", value="HARMS")
        dob = st.date_input("Date de naissance (DOB)", value=datetime.date(1995, 3, 15))
    with col2:
        fn = st.text_input("Prénom (FN)", value="ROSA")
        sex = st.selectbox("Sexe (SEX)", ["M", "F", "X"], index=1)
    with col3:
        st.write("")  # espace visuel
        st.write("")
        st.write("")

    col4, col5, col6 = st.columns(3)
    with col4:
        hgt_feet = st.number_input("Taille - pieds", min_value=0, max_value=8, value=5)
    with col5:
        hgt_inches = st.number_input("Taille - pouces", min_value=0, max_value=11, value=10)
    with col6:
        wgt = st.number_input("Poids (lbs)", min_value=50, max_value=400, value=160)

    col7, col8 = st.columns(2)
    with col7:
        hair = st.text_input("Cheveux (HAIR, 3 lettres)", value="BRN")
    with col8:
        eyes = st.text_input("Yeux (EYES, 3 lettres)", value="BLU")

    col9, col10 = st.columns(2)
    with col9:
        iss = st.date_input("Date d’émission (ISS)", value=datetime.date(2024, 6, 10))
    with col10:
        fo = st.selectbox("Bureau (Field Office)", [
            "San Jose (654) - Silicon Valley",
            "Fresno (210) - Central Valley",
            "Oakland (987) - East Bay",
            "Riverside (543) - Inland Empire",
            "Santa Ana (876) - Orange County"
        ])

    col11, col12, col13 = st.columns(3)
    with col11:
        class_ = st.text_input("Classe (CLASS)", value="C")
    with col12:
        rstr = st.text_input("Restrictions (RSTR)", value="NONE")
    with col13:
        end = st.text_input("Endorsements (END)", value="")

    submit = st.form_submit_button("⚙️ Générer l'aperçu")

# -------------------------
# Rendu UI/UX (aucun code affiché)
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

    # Données résultat (internes, non affichées comme code)
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

    # Aperçu visuel construit avec composants Streamlit (pas de code source affiché)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div style='display:flex; justify-content:space-between; align-items:center;'>"
                f"<div><h3 style='margin:0'>Aperçu officiel</h3><div class='sub'>Aperçu visuel du permis</div></div>"
                f"<div class='badge'>DL #{dl_number}</div>"
                "</div>", unsafe_allow_html=True)

    # Carte principale (layout Streamlit)
    container = st.container()
    with container:
        cols = st.columns([0.36, 0.64])
        with cols[0]:
            st.markdown("<div class='card dl-left'>", unsafe_allow_html=True)
            st.markdown("<div class='dl-photo'>Photo</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='dl-meta' style='margin-top:12px'>Bureau</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='value' style='margin-top:6px'>{result['FO']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='dl-meta' style='margin-top:12px'>Document ID</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='sub' style='margin-top:6px'>{result['DD']}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with cols[1]:
            st.markdown("<div class='card dl-right'>", unsafe_allow_html=True)
            # Ligne nom / sexe
            st.markdown("<div class='row'>", unsafe_allow_html=True)
            left, right = st.columns([0.7, 0.3])
            with left:
                st.markdown("<div class='label'>Nom</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='value'>{result['LN']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='sub'>Prénom: {result['FN']}</div>", unsafe_allow_html=True)
            with right:
                st.markdown("<div class='label'>Sexe</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='value' style='text-align:right'>{result['SEX']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='sub' style='text-align:right'>Né(e): {result['DOB']}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Taille / Yeux-Cheveux
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.markdown("<div class='row'>", unsafe_allow_html=True)
            left2, right2 = st.columns([0.6, 0.4])
            with left2:
                st.markdown("<div class='label'>Taille</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='value'>{result['HGT']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='sub'>Poids: {result['WGT']}</div>", unsafe_allow_html=True)
            with right2:
                st.markdown("<div class='label' style='text-align:right'>Yeux / Cheveux</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='value' style='text-align:right'>{result['EYES']} / {result['HAIR']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='sub' style='text-align:right'>Classe: {result['CLASS']}</div>", unsafe_allow_html=True)
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

            # Meta
            st.markdown(f"<div class='meta'>Généré le: {result['GENERATED_AT']}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Message final — pas de code source affiché, aperçu uniquement
    st.success("✅ Aperçu affiché — le code source n'est pas visible publiquement.")
