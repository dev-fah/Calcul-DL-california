# driver_licence_americain.py
# UI/UX améliorée pour l'aperçu (preview) — prêt à coller
# Dépendances (pour info) : streamlit, pandas, openpyxl
# Installer localement : pip install streamlit pandas openpyxl

import streamlit as st
import pandas as pd
import json
import datetime
import hashlib
import random
from io import BytesIO
import traceback

st.set_page_config(page_title="Générateur DL et DD — Aperçu optimisé", layout="wide")

# -----------------------
# Styles CSS pour une preview plus lisible et compacte
# -----------------------
st.markdown(
    """
    <style>
    /* Conteneur principal : largeur confortable */
    .main .block-container {
        max-width: 980px;
        padding-top: 0.8rem;
        padding-bottom: 0.8rem;
    }

    /* Compact widgets spacing */
    .stForm, .stForm > div > div {
        gap: 0.25rem;
    }

    /* Inputs compact */
    input[type="text"], input[type="number"], .stDateInput>div>input {
        padding: 6px 8px;
        height: 36px;
        font-size: 14px;
    }

    /* Buttons compact */
    .stButton>button {
        padding: 6px 12px;
        height: 36px;
        font-size: 14px;
    }

    /* Headings spacing */
    h1, h2, h3 {
        margin-top: 0.25rem;
        margin-bottom: 0.25rem;
    }

    /* DataFrame smaller font and denser rows */
    .stDataFrame table {
        font-size: 13px;
    }

    /* Card-like preview boxes */
    .preview-card {
        border-radius: 8px;
        padding: 10px 12px;
        background: #f8fafc;
        box-shadow: 0 1px 2px rgba(16,24,40,0.04);
        margin-bottom: 8px;
    }

    /* Key-value pair style */
    .kv-label { color: #6b7280; font-size:13px; }
    .kv-value { font-weight:600; font-size:15px; }

    /* Sidebar width best-effort */
    .css-1d391kg { max-width: 300px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------
# Utilitaires
# -----------------------
def deterministic_seed(*parts: str) -> int:
    key = "|".join([p or "" for p in parts])
    h = hashlib.md5(key.encode("utf-8")).hexdigest()
    return int(h[:8], 16)

def random_letters(rnd: random.Random, length: int) -> str:
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join(rnd.choice(letters) for _ in range(length))

def random_digits(rnd: random.Random, length: int) -> str:
    digits = "0123456789"
    return "".join(rnd.choice(digits) for _ in range(length))

def format_height(feet: int, inches: int) -> str:
    return f"{feet}'-{inches:02d}\""

def to_json_bytes(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")

def to_excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Résultats")
    return buffer.getvalue()

def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

# -----------------------
# Sidebar : Paramètres avancés
# -----------------------
with st.sidebar:
    st.header("Paramètres avancés")
    c1, c2 = st.columns([1, 1])
    with c1:
        sec_len = st.number_input("Longueur SEC", min_value=1, max_value=10, value=2, step=1, help="Lettres")
    with c2:
        batch_len = st.number_input("Longueur BATCH", min_value=1, max_value=10, value=5, step=1, help="Chiffres")
    st.markdown("---")
    st.caption("UI épurée : détails techniques inclus dans l'export.")

# -----------------------
# Formulaire principal (compact)
# -----------------------
st.title("Générateur DL et DD")
st.markdown("Champs et aperçu optimisés pour une lecture claire et rapide.")

with st.form(key="form_main"):
    left, right = st.columns([2, 1], gap="small")

    with left:
        r1c1, r1c2, r1c3 = st.columns([1.6, 1.2, 1])
        with r1c1:
            ln = st.text_input("Nom de famille (LN)", value="Harms")
        with r1c2:
            fn = st.text_input("Prénom (FN)", value="Rosa")
        with r1c3:
            sex = st.selectbox("Sexe (SEX)", ["M", "F", "Autre"], index=0)

        r2c1, r2c2, r2c3 = st.columns([1.2, 1, 1])
        with r2c1:
            dob = st.date_input("Date de naissance (DOB)", value=datetime.date(1990, 12, 31))
        with r2c2:
            hgt_feet = st.number_input("Taille - pieds", min_value=0, max_value=8, value=5)
        with r2c3:
            hgt_inches = st.number_input("Taille - pouces", min_value=0, max_value=11, value=8)

        r3c1, r3c2 = st.columns([1.5, 1])
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
        st.subheader("Génération")
        st.metric(label="SEC len", value=sec_len)
        st.metric(label="BATCH len", value=batch_len)
        st.markdown("---")
        st.subheader("Export")
        export_format = st.selectbox("Format", ["JSON", "CSV", "XLSX"], index=0)
        calculate = st.form_submit_button("Calculer", use_container_width=True)

st.info("Note : l’export PDF est désactivé dans cet environnement.")

# -----------------------
# Traitement et Aperçu UI/UX amélioré
# -----------------------
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
            "LN": ln,
            "FN": fn,
            "SEX": sex,
            "HGT": hgt,
            "DOB": dob.isoformat(),
            "WGT": wgt,
            "ISS": iss.isoformat(),
            "EXP": exp_date.isoformat(),
            "EXP_ALT": exp_alt_date.isoformat(),
            "HAIR": hair,
            "EYES": eyes,
            "FO": fo,
            "CLASS": class_,
            "RSTR": rstr,
            "END": end,
            "DL_NUMBER": dl_number,
            "BATCH": batch,
            "SEC": sec,
            "SEQ": seq,
            "GENERATED_AT": datetime.datetime.utcnow().isoformat() + "Z"
        }

        # ---------- Aperçu UI/UX ----------
        st.subheader("Aperçu")
        # Card row with key values for quick scan
        c1, c2, c3, c4 = st.columns([1.2, 1, 1, 1])
        with c1:
            st.markdown('<div class="preview-card"><div class="kv-label">Nom</div><div class="kv-value">{}</div></div>'.format(result["LN"]), unsafe_allow_html=True)
            st.markdown('<div class="preview-card"><div class="kv-label">Prénom</div><div class="kv-value">{}</div></div>'.format(result["FN"]), unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="preview-card"><div class="kv-label">Sexe</div><div class="kv-value">{}</div></div>'.format(result["SEX"]), unsafe_allow_html=True)
            st.markdown('<div class="preview-card"><div class="kv-label">Taille</div><div class="kv-value">{}</div></div>'.format(result["HGT"]), unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="preview-card"><div class="kv-label">Date de naissance</div><div class="kv-value">{}</div></div>'.format(result["DOB"]), unsafe_allow_html=True)
            st.markdown('<div class="preview-card"><div class="kv-label">Poids</div><div class="kv-value">{}</div></div>'.format(result["WGT"]), unsafe_allow_html=True)
        with c4:
            st.markdown('<div class="preview-card"><div class="kv-label">Issu / Exp</div><div class="kv-value">{}</div><div style="font-size:12px;color:#6b7280">{}</div></div>'.format(result["ISS"], result["EXP"]), unsafe_allow_html=True)
            st.markdown('<div class="preview-card"><div class="kv-label">DL Number</div><div class="kv-value">{}</div></div>'.format(result["DL_NUMBER"]), unsafe_allow_html=True)

        # Compact table with essential columns
        st.markdown("**Tableau récapitulatif**")
        df = pd.DataFrame([{
            "LN": result["LN"],
            "FN": result["FN"],
            "SEX": result["SEX"],
            "HGT": result["HGT"],
            "DOB": result["DOB"],
            "WGT": result["WGT"],
            "ISS": result["ISS"],
            "EXP": result["EXP"],
            "CLASS": result["CLASS"],
            "RSTR": result["RSTR"],
            "DL_NUMBER": result["DL_NUMBER"]
        }])
        st.dataframe(df, use_container_width=True, height=160)

        # Détails techniques dans un expander (non intrusif)
        with st.expander("Détails techniques (BATCH / SEC / SEQ)", expanded=False):
            st.json({
                "BATCH": result["BATCH"],
                "SEC": result["SEC"],
                "SEQ": result["SEQ"],
                "GENERATED_AT": result["GENERATED_AT"]
            })

        # Export
        if export_format == "JSON":
            data_bytes = to_json_bytes(result)
            mime = "application/json"
            filename = "dl_dd_generated.json"
        elif export_format == "CSV":
            data_bytes = to_csv_bytes(pd.DataFrame([result]))
            mime = "text/csv"
            filename = "dl_dd_generated.csv"
        else:
            data_bytes = to_excel_bytes(pd.DataFrame([result]))
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = "dl_dd_generated.xlsx"

        st.download_button(
            label=f"Télécharger ({export_format})",
            data=data_bytes,
            file_name=filename,
            mime=mime
        )

        st.success("Génération terminée — télécharge le fichier si besoin.")

    except Exception:
        st.error("Une erreur est survenue lors de la génération.")
        st.text(traceback.format_exc())
