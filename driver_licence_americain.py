# driver_licence_americain.py
# UI/UX : bouton de téléchargement avec icône intégrée (HTML download link)
# Dépendances (pour info) : streamlit, pandas, openpyxl
# pip install streamlit pandas openpyxl

import streamlit as st
import pandas as pd
import datetime
import hashlib
import random
import json
import base64
from io import BytesIO

st.set_page_config(page_title="Générateur DL — Bouton téléchargement avec icône", layout="wide")

# Icône fournie par l'utilisateur
DOWNLOAD_ICON_URL = "https://img.icons8.com/external-anggara-glyph-anggara-putra/32/external-download-music-audio-anggara-glyph-anggara-putra.png"

# -------------------------
# CSS pour UI moderne & bouton custom
# -------------------------
st.markdown("""
<style>
.main .block-container { max-width: 980px; padding-top: 0.8rem; padding-bottom: 0.8rem; }
body { background: linear-gradient(180deg,#f7fbff 0%, #ffffff 100%); }

/* Card style */
.card { background:#fff; border-radius:12px; padding:12px; box-shadow:0 6px 18px rgba(15,23,42,0.06); margin-bottom:10px; }
.kv-label { color:#6b7280; font-size:13px; margin-bottom:4px; }
.kv-value { font-weight:700; font-size:16px; color:#0f172a; }

/* Inputs compact */
.stTextInput>div>div>input, .stNumberInput>div>input, .stSelectbox>div>div { padding:8px 10px; height:40px; font-size:14px; }

/* Primary button style */
.stButton>button {
    background: linear-gradient(90deg,#2563eb,#7c3aed);
    color:white;
    border-radius:10px;
    padding:8px 16px;
    font-weight:600;
    box-shadow:0 6px 14px rgba(37,99,235,0.12);
}

/* Custom download link styled as button with icon */
.download-btn {
    display:inline-flex;
    align-items:center;
    gap:8px;
    background: linear-gradient(90deg,#06b6d4,#0ea5e9);
    color: #fff !important;
    padding:8px 14px;
    border-radius:10px;
    text-decoration:none;
    font-weight:600;
    box-shadow:0 6px 14px rgba(6,182,212,0.12);
}
.download-btn img { display:inline-block; vertical-align:middle; }

/* Alignement horizontal des boutons dans un container */
.button-row { display:flex; gap:12px; justify-content:flex-end; align-items:center; }

/* Small helpers */
.stDataFrame table { font-size:13px; }
.css-1d391kg { max-width: 300px; } /* sidebar best-effort */
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

def random_letters(rnd: random.Random, length: int) -> str:
    return "".join(rnd.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(length))

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
# Sidebar : paramètres avancés
# -------------------------
with st.sidebar:
    st.header("Paramètres avancés")
    c1, c2 = st.columns([1, 1])
    with c1:
        sec_len = st.number_input("Longueur SEC", min_value=1, max_value=6, value=2, step=1, help="Nombre de lettres SEC")
    with c2:
        batch_len = st.number_input("Longueur BATCH", min_value=1, max_value=8, value=5, step=1, help="Nombre de chiffres BATCH")
    st.markdown("---")
    st.caption("Aperçu visuel — tableau récapitulatif désactivé.")

# -------------------------
# Formulaire principal
# -------------------------
st.title("Générateur DL et DD")
st.markdown("Interface optimisée — bouton de téléchargement avec icône intégré.")

with st.form(key="form_main"):
    left, right = st.columns([2.2, 1], gap="small")

    with left:
        r1c1, r1c2, r1c3 = st.columns([1.6, 1.2, 0.9])
        with r1c1:
            ln = st.text_input("Nom de famille (LN)", value="Harms")
        with r1c2:
            fn = st.text_input("Prénom (FN)", value="Rosa")
        with r1c3:
            sex = st.selectbox("Sexe (SEX)", ["M", "F", "Autre"], index=0)

        r2c1, r2c2, r2c3 = st.columns([1.2, 0.9, 0.9])
        with r2c1:
            dob = st.date_input("Date de naissance (DOB)", value=datetime.date(1995, 12, 14))
        with r2c2:
            hgt_feet = st.number_input("Taille - pieds", min_value=0, max_value=8, value=5)
        with r2c3:
            hgt_inches = st.number_input("Taille - pouces", min_value=0, max_value=11, value=8)

        r3c1, r3c2 = st.columns([1.6, 1])
        with r3c1:
            wgt = st.text_input("Poids (WGT)", value="175 lb")
        with r3c2:
            iss = st.date_input("Date d’émission (ISS)", value=datetime.date(2015, 9, 30))

        r4c1, r4c2, r4c3 = st.columns([1, 1, 1])
        with r4c1:
            hair = st.text_input("Cheveux (HAIR)", value="BRN")
        with r4c2:
            eyes = st.text_input("Yeux (EYES)", value="BRO")
        with r4c3:
            fo = st.text_input("Bureau (Field Office)", value="Pasadena (509)")

        r5c1, r5c2, r5c3 = st.columns([1, 1, 1])
        with r5c1:
            class_ = st.text_input("Classe (CLASS)", value="C")
        with r5c2:
            rstr = st.text_input("Restrictions (RSTR)", value="NONE")
        with r5c3:
            end = st.text_input("Endorsements (END)", value="")

    with right:
        st.markdown("### Actions")
        st.metric(label="SEC len", value=sec_len)
        st.metric(label="BATCH len", value=batch_len)
        st.markdown("---")
        export_format = st.selectbox("Format d'export", ["JSON", "CSV", "XLSX"])
        b1, b2, b3 = st.columns([0.2, 1, 0.2])
        with b2:
            calculate = st.form_submit_button("Calculer")

st.info("Note : le tableau récapitulatif est désactivé — l'aperçu est présenté en cartes.")

# -------------------------
# Traitement et Aperçu (cartes seulement) avec icône sur le bouton Télécharger
# -------------------------
if calculate:
    try:
        seed = deterministic_seed(ln, fn, dob.isoformat())
        rnd = random.Random(seed)

        batch = random_digits(rnd, batch_len)
        sec = random_letters(rnd, sec_len)
        seq = random_digits(rnd, 6)

        try:
            exp_date = iss.replace(year=iss.year + 5)
        except Exception:
            exp_date = iss
        try:
            exp_alt_date = iss.replace(year=iss.year + 8)
        except Exception:
            exp_alt_date = exp_date

        dl_number = f"{(ln or '')[:2].upper()}{(fn or '')[:2].upper()}{batch}{seq}"
        hgt = format_height(int(hgt_feet), int(hgt_inches))

        result = {
            "LN": ln, "FN": fn, "SEX": sex, "HGT": hgt, "DOB": dob.isoformat(),
            "WGT": wgt, "ISS": iss.isoformat(), "EXP": exp_date.isoformat(),
            "EXP_ALT": exp_alt_date.isoformat(), "HAIR": hair, "EYES": eyes,
            "FO": fo, "CLASS": class_, "RSTR": rstr, "END": end,
            "DL_NUMBER": dl_number, "BATCH": batch, "SEC": sec, "SEQ": seq,
            "GENERATED_AT": datetime.datetime.utcnow().isoformat() + "Z"
        }

        # ---------- Aperçu visuel (cartes) ----------
        st.subheader("Aperçu")
        c1, c2, c3, c4 = st.columns([1.2, 1, 1, 1], gap="small")
        with c1:
            st.markdown(f"<div class='card'><div class='kv-label'>Nom</div><div class='kv-value'>{result['LN']}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><div class='kv-label'>Prénom</div><div class='kv-value'>{result['FN']}</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='card'><div class='kv-label'>Sexe</div><div class='kv-value'>{result['SEX']}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><div class='kv-label'>Taille</div><div class='kv-value'>{result['HGT']}</div></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='card'><div class='kv-label'>Date de naissance</div><div class='kv-value'>{result['DOB']}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><div class='kv-label'>Poids</div><div class='kv-value'>{result['WGT']}</div></div>", unsafe_allow_html=True)
        with c4:
            st.markdown(f"<div class='card'><div class='kv-label'>Issu / Exp</div><div class='kv-value'>{result['ISS']} → {result['EXP']}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><div class='kv-label'>DL Number</div><div class='kv-value'>{result['DL_NUMBER']}</div></div>", unsafe_allow_html=True)

        # ---------- Détails techniques (expander non intrusif) ----------
        with st.expander("Détails techniques (BATCH / SEC / SEQ)", expanded=False):
            st.json({"BATCH": result["BATCH"], "SEC": result["SEC"], "SEQ": result["SEQ"], "GENERATED_AT": result["GENERATED_AT"]})

        # ---------- Préparer les données d'export ----------
        if export_format == "JSON":
            data_bytes = to_json_bytes(result); mime = "application/json"; fname = "dl_dd_generated.json"
        elif export_format == "CSV":
            data_bytes = to_csv_bytes(pd.DataFrame([result])); mime = "text/csv"; fname = "dl_dd_generated.csv"
        else:
            data_bytes = to_excel_bytes(pd.DataFrame([result])); mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"; fname = "dl_dd_generated.xlsx"

        # Convertir en base64 pour créer un lien data URI (sécurisé côté client)
        b64 = base64.b64encode(data_bytes).decode()
        data_href = f"data:{mime};base64,{b64}"

        # ---------- Afficher le bouton de téléchargement avec l'icône intégré ----------
        # On aligne le bouton à droite en utilisant des colonnes
        spacer, btn_col = st.columns([3, 1])
        with btn_col:
            # HTML link styled as button, contenant l'icône et le label
            html = f'''
                <a class="download-btn" href="{data_href}" download="{fname}">
                    <img src="{DOWNLOAD_ICON_URL}" width="20" height="20" alt="download icon" />
                    <span>Télécharger</span>
                </a>
            '''
            st.markdown(html, unsafe_allow_html=True)

        st.success("Génération terminée — télécharge le fichier si besoin.")

    except Exception as e:
        st.error("Une erreur est survenue lors de la génération.")
        st.text(str(e))
