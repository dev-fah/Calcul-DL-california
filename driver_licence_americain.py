# driver_licence_americain.py
# UI optimisée : tailles et espacements ajustés pour une meilleure UX
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

# --- Configuration page et style CSS pour contrôler largeur et espacement ---
st.set_page_config(page_title="Générateur DL et DD", layout="wide")

# CSS pour améliorer l'UI : limiter la largeur, réduire marges et rendre les inputs plus compacts
st.markdown(
    """
    <style>
    /* Conteneur principal : limite la largeur pour une lecture confortable */
    .main .block-container {
        max-width: 980px;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    /* Réduire l'espace vertical entre les widgets */
    .stForm, .stForm > div > div {
        gap: 0.25rem;
    }

    /* Rendre les labels et inputs plus compacts */
    .stTextInput>div>div>input, .stNumberInput>div>input, .stSelectbox>div>div {
        padding: 6px 8px;
        height: 36px;
    }

    /* Boutons plus compacts */
    .stButton>button {
        padding: 6px 12px;
        height: 36px;
    }

    /* Réduire l'espace des en-têtes */
    h1, h2, h3 {
        margin-top: 0.25rem;
        margin-bottom: 0.25rem;
    }

    /* Tableau d'aperçu : police plus petite pour tenir dans l'écran */
    .stDataFrame table {
        font-size: 13px;
    }

    /* Sidebar largeur raisonnable */
    .css-1d391kg { max-width: 300px; } /* class may vary across versions; this is a best-effort */
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------
# Fonctions utilitaires
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
# Sidebar : Paramètres avancés (compact)
# -----------------------
with st.sidebar:
    st.header("Paramètres avancés")
    # Utiliser colonnes compactes dans la sidebar
    c1, c2 = st.columns([1, 1])
    with c1:
        sec_len = st.number_input("Longueur SEC", min_value=1, max_value=10, value=2, step=1, help="Lettres")
    with c2:
        batch_len = st.number_input("Longueur BATCH", min_value=1, max_value=10, value=5, step=1, help="Chiffres")
    st.markdown("---")
    st.caption("UI épurée : détails techniques inclus dans l'export.")

# -----------------------
# Main UI : Formulaire compact et organisé en colonnes
# -----------------------
st.title("Générateur DL et DD")
st.markdown("UI optimisée — champs redimensionnés pour une meilleure lisibilité et ergonomie.")

# Formulaire en deux colonnes principales pour réduire hauteur et améliorer scannabilité
with st.form(key="form_main"):
    left, right = st.columns([2, 1], gap="small")

    with left:
        st.subheader("Données personnelles")
        # Grouper les champs en lignes pour réduire hauteur
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
        st.markdown("Paramètres rapides")
        st.write("")  # petit espace
        # Afficher valeurs techniques compactes
        st.metric(label="SEC len", value=sec_len)
        st.metric(label="BATCH len", value=batch_len)
        st.markdown("---")
        st.subheader("Export")
        export_format = st.selectbox("Format", ["JSON", "CSV", "XLSX"], index=0)
        st.write("")  # espace
        calculate = st.form_submit_button("Calculer", use_container_width=True)

# Note visible
st.info("Note : l’export PDF est désactivé dans cet environnement.")

# -----------------------
# Traitement après soumission
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

        # Affichage résumé compact
        st.subheader("Aperçu")
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
        st.dataframe(df, use_container_width=True)

        st.markdown("### Détails techniques")
        st.json({
            "BATCH": result["BATCH"],
            "SEC": result["SEC"],
            "SEQ": result["SEQ"]
        })

        # Préparer export
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
