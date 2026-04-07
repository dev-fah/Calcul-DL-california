# driver_licence_uiux_no_photo_preview.py
# Aperçu UI/UX sans bloc "Photo" — aperçu visuel remplaçant la photo
# Dépendances : streamlit, pandas
# Installation : pip install streamlit pandas

import streamlit as st
import pandas as pd
import datetime
import hashlib
import random
from io import BytesIO
import json

st.set_page_config(page_title="Aperçu Permis - UI/UX", layout="wide")

# -------------------------
# CSS pour l'aperçu visuel (sans photo)
# -------------------------
st.markdown(
    """
    <style>
    :root{
      --bg: #f6f8fb;
      --card: #ffffff;
      --accent: #2563eb;
      --accent2: #7c3aed;
      --muted: #6b7280;
      --shadow: 0 10px 30px rgba(2,6,23,0.08);
    }
    body { background: var(--bg); font-family: "Segoe UI", Roboto, Arial, sans-serif; color:#0f172a; }
    .page { padding:18px 24px; }
    .form-card { background: var(--card); border-radius:12px; padding:16px; box-shadow: var(--shadow); margin-bottom:18px; }
    .preview-card { background: linear-gradient(180deg,#ffffff,#f8fafc); border-radius:12px; padding:18px; box-shadow: var(--shadow); }
    .dl-wrapper { display:flex; gap:18px; align-items:flex-start; }
    .dl-left { width:36%; min-width:240px; border-radius:10px; padding:14px; background: linear-gradient(135deg, rgba(37,99,235,0.04), rgba(124,58,237,0.02)); }
    .dl-left .brand { font-weight:800; color:var(--accent); font-size:14px; margin-bottom:8px; }
    .dl-left .mini-graphic { width:100%; height:120px; border-radius:8px; background: linear-gradient(90deg,#e6eefc,#f3eefe); display:flex; align-items:center; justify-content:center; color:var(--muted); font-weight:700; }
    .dl-left .info { margin-top:12px; }
    .dl-left .label { font-size:12px; color:var(--muted); }
    .dl-left .value { font-size:14px; font-weight:700; color:#0f172a; margin-top:4px; }
    .dl-right { flex:1; display:flex; flex-direction:column; gap:10px; }
    .row { display:flex; justify-content:space-between; gap:12px; align-items:center; }
    .col { display:flex; flex-direction:column; gap:4px; }
    .label { font-size:12px; color:var(--muted); }
    .value { font-size:16px; color:#0f172a; font-weight:800; }
    .sub { font-size:13px; color:var(--muted); }
    .badge { background: linear-gradient(90deg,var(--accent),var(--accent2)); color:white; padding:6px 10px; border-radius:999px; font-weight:800; }
    .meta { font-size:12px; color:var(--muted); margin-top:8px; }
    .small-gap { height:8px; }
    @media (max-width: 880px) {
      .dl-wrapper { flex-direction:column; }
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

def to_json_bytes(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")

def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

def to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Résultats")
    return buf.getvalue()

# -------------------------
# Formulaire d'entrée
# -------------------------
st.title("Générateur Permis — Aperçu UI/UX (sans photo)")
st.caption("Les informations ci‑dessous alimentent l'aperçu visuel. Modifie les champs puis clique Générer.")

with st.form(key="form_main"):
    st.markdown("<div class='form-card'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.2, 1.2, 0.8])
    with c1:
        ln = st.text_input("Nom de famille (LN)", value="HARMS")
        dob = st.date_input("Date de naissance (DOB)", value=datetime.date(1995, 3, 15))
    with c2:
        fn = st.text_input("Prénom (FN)", value="ROSA")
        sex = st.selectbox("Sexe (SEX)", ["M", "F", "X"], index=1)
    with c3:
        st.write("")  # espace
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
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Génération et rendu de l'aperçu (sans photo)
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

    # Aperçu visuel : remplace le bloc photo par une mini-illustration / aperçu stylisé
    st.markdown("<div class='preview-card'>", unsafe_allow_html=True)
    st.markdown("<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;'>"
                f"<div><h3 style='margin:0'>Aperçu officiel</h3><div class='sub' style='margin-top:4px'>Aperçu visuel (bloc photo remplacé)</div></div>"
                f"<div class='badge'>DL #{dl_number}</div>"
                "</div>", unsafe_allow_html=True)

    # Structure de la carte (gérée par colonnes Streamlit pour alignement précis)
    container = st.container()
    with container:
        cols = st.columns([0.36, 0.64])
        with cols[0]:
            # Bloc remplaçant la photo : mini-illustration + informations bureau / document id
            st.markdown("<div class='dl-left'>", unsafe_allow_html=True)
            st.markdown("<div class='brand'>IDENTIFICATION</div>", unsafe_allow_html=True)
            st.markdown("<div class='mini-graphic'>APERÇU VISUEL</div>", unsafe_allow_html=True)
            st.markdown("<div class='info'>", unsafe_allow_html=True)
            st.markdown("<div class='label'>Bureau</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='value'>{result['FO']}</div>", unsafe_allow_html=True)
            st.markdown("<div class='small-gap'></div>", unsafe_allow_html=True)
            st.markdown("<div class='label'>Document ID</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='sub'>{result['DD']}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with cols[1]:
            st.markdown("<div class='dl-right'>", unsafe_allow_html=True)

            # Ligne Nom / Sexe
            left, right = st.columns([0.7, 0.3])
            with left:
                st.markdown("<div class='label'>Nom</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='value'>{result['LN']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='sub'>Prénom: {result['FN']}</div>", unsafe_allow_html=True)
            with right:
                st.markdown("<div class='label' style='text-align:right'>Sexe</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='value' style='text-align:right'>{result['SEX']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='sub' style='text-align:right'>Né(e): {result['DOB']}</div>", unsafe_allow_html=True)

            # Taille / Yeux-Cheveux
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            left2, right2 = st.columns([0.6, 0.4])
            with left2:
                st.markdown("<div class='label'>Taille</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='value'>{result['HGT']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='sub'>Poids: {result['WGT']}</div>", unsafe_allow_html=True)
            with right2:
                st.markdown("<div class='label' style='text-align:right'>Yeux / Cheveux</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='value' style='text-align:right'>{result['EYES']} / {result['HAIR']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='sub' style='text-align:right'>Classe: {result['CLASS']}</div>", unsafe_allow_html=True)

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

    # Message final simple
    st.success("Aperçu mis à jour — le bloc photo a été remplacé par un aperçu visuel modifiable.")
