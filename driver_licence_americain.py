# driver_licence_americain.py
# Interface "Générateur DL et DD" complète et autonome (sans export PDF)
# Paquets requis : streamlit, pandas, pillow (optionnel pour l'aperçu photo), openpyxl (si tu veux XLSX)
# Exemple d'installation locale : pip install streamlit pandas pillow openpyxl

import streamlit as st
import pandas as pd
import json
import datetime
import hashlib
import random
from io import BytesIO
from PIL import Image, ImageOps
import traceback

st.set_page_config(page_title="Générateur DL et DD", layout="wide")

# -----------------------
# Fonctions utilitaires
# -----------------------
def deterministic_seed(*parts: str) -> int:
    """Retourne un entier déterministe basé sur les parties de chaîne fournies."""
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

def iso_date(d: datetime.date) -> str:
    return d.isoformat()

def build_dd_from_template(template: str, values: dict) -> str:
    """
    Remplace les placeholders {{ISS}},{{FO}},{{BATCH}},{{EXP_ALT}},{{SEC}},{{SEQ}},{{EXP}} dans le template.
    Si un placeholder manque, on le laisse vide.
    """
    out = template
    replacements = {
        "{{ISS}}": values.get("ISS", ""),
        "{{FO}}": values.get("FO", ""),
        "{{BATCH}}": values.get("BATCH", ""),
        "{{EXP_ALT}}": values.get("EXP_ALT", ""),
        "{{SEC}}": values.get("SEC", ""),
        "{{SEQ}}": values.get("SEQ", ""),
        "{{EXP}}": values.get("EXP", "")
    }
    for k, v in replacements.items():
        out = out.replace(k, str(v))
    return out

def to_json_bytes(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")

# -----------------------
# Sidebar : Paramètres avancés
# -----------------------
with st.sidebar:
    st.header("Paramètres avancés")
    sec_len = st.number_input("Longueur SEC (lettres)", min_value=1, max_value=10, value=2, step=1)
    batch_len = st.number_input("Longueur BATCH (chiffres)", min_value=1, max_value=10, value=5, step=1)
    st.markdown("**Template DD (placeholders: {{ISS}},{{FO}},{{BATCH}},{{EXP_ALT}},{{SEC}},{{SEQ}},{{EXP}})**")
    default_template = "{{ISS}}{{BATCH}}{{EXP}}{{SEC}}{{EXP_ALT}}"
    template_dd = st.text_area("Template DD", value=default_template, height=120)
    st.markdown("---")
    st.caption("UI épurée : les détails techniques sont inclus dans l’export.")

# -----------------------
# Main UI : Formulaire
# -----------------------
st.title("Générateur DL et DD")
st.markdown("UI épurée : les détails techniques sont inclus dans l’export. Choisissez le format d’export dans le menu principal.")

col_main, col_photo = st.columns([3, 1])

with col_main:
    with st.form(key="form_main"):
        st.subheader("Données personnelles")
        ln = st.text_input("Nom de famille (LN)", value="Harms")
        fn = st.text_input("Prénom (FN)", value="Rosa")
        sex = st.selectbox("Sexe (SEX)", ["M", "F", "Autre"], index=0)
        dob = st.date_input("Date de naissance (DOB, YYYY-MM-DD)", value=datetime.date(1990, 12, 31))
        # Taille en pieds/pouces
        hgt_feet = st.number_input("Taille - pieds", min_value=0, max_value=8, value=5)
        hgt_inches = st.number_input("Taille - pouces", min_value=0, max_value=11, value=8)
        wgt = st.text_input("Poids (WGT)", value="175 lb")
        iss = st.date_input("Date d’émission (ISS, YYYY-MM-DD)", value=datetime.date(2015, 9, 30))
        hair = st.text_input("Cheveux (HAIR)", value="BRN")
        eyes = st.text_input("Yeux (EYES)", value="BRO")
        fo = st.text_input("Bureau (Field Office)", value="Pasadena (509)")
        class_ = st.text_input("Classe (CLASS)", value="C")
        rstr = st.text_input("Restrictions (RSTR)", value="NONE")
        end = st.text_input("Endorsements (END)", value="")
        st.markdown("---")
        st.subheader("Export")
        export_format = st.selectbox("Choisir le format d’export", ["JSON"], index=0)
        calculate = st.form_submit_button("Calculer")

with col_photo:
    st.markdown("### Photo (optionnelle)")
    photo = st.file_uploader("", type=["jpg", "jpeg", "png"])
    if photo:
        try:
            img = Image.open(photo)
            img = ImageOps.exif_transpose(img)
            img = ImageOps.fit(img, (300, 300))
            st.image(img, caption="Aperçu photo", use_column_width=False)
        except Exception:
            st.warning("Impossible d'afficher l'image fournie.")

# Note visible sur l'interface
st.info("Note : l’export PDF est désactivé car le module 'reportlab' n’est pas installé sur cet environnement. Installez 'reportlab' pour activer l’export PDF.")

# -----------------------
# Traitement après soumission
# -----------------------
if calculate:
    try:
        # Seed déterministe basé sur nom+prénom+dob pour reproductibilité
        seed = deterministic_seed(ln, fn, dob.isoformat())
        rnd = random.Random(seed)

        # Génération des éléments techniques
        batch = random_digits(rnd, batch_len)
        sec = random_letters(rnd, sec_len)
        seq = random_digits(rnd, 6)  # séquence interne (6 chiffres par défaut)
        # Expiration standard : ISS + 5 ans (exemple)
        exp_date = iss.replace(year=iss.year + 5)
        # Alternative d'expiration (EXP_ALT) : ISS + 8 ans (exemple)
        try:
            exp_alt_date = iss.replace(year=iss.year + 8)
        except Exception:
            # fallback si date invalide (ex: 29 février)
            exp_alt_date = exp_date

        # Construire valeurs pour template
        values = {
            "ISS": iss.strftime("%Y%m%d"),
            "FO": fo,
            "BATCH": batch,
            "EXP": exp_date.strftime("%Y%m%d"),
            "EXP_ALT": exp_alt_date.strftime("%Y%m%d"),
            "SEC": sec,
            "SEQ": seq
        }

        # Générer DD via template
        dd_generated = build_dd_from_template(template_dd, values)

        # Générer numéro DL simulé (ex: combinaison déterministe)
        dl_number = f"{ln[:2].upper()}{fn[:2].upper()}{batch}{seq}"

        # Construire l'objet de sortie
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
            "DD_TEMPLATE": template_dd,
            "DD_GENERATED": dd_generated,
            "GENERATED_AT": datetime.datetime.utcnow().isoformat() + "Z"
        }

        # Affichage
        st.subheader("Aperçu des données générées")
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
        st.dataframe(df)

        st.markdown("### Détails techniques (inclus dans l'export)")
        st.json({
            "BATCH": result["BATCH"],
            "SEC": result["SEC"],
            "SEQ": result["SEQ"],
            "DD_GENERATED": result["DD_GENERATED"]
        })

        # Préparer export JSON
        json_bytes = to_json_bytes(result)
        st.download_button(
            label=f"Télécharger ({export_format})",
            data=json_bytes,
            file_name="dl_dd_generated.json",
            mime="application/json"
        )

        st.success("Génération terminée — télécharge le fichier si besoin.")

    except Exception:
        st.error("Une erreur est survenue lors de la génération.")
        st.text(traceback.format_exc())
