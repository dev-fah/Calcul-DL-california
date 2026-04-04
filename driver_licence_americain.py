import streamlit as st
import html
import re
import json
from datetime import date, datetime
import hashlib

# ---------------------------
# app.py - Version finale complète
# - Champs avec labels visibles
# - Infobulles stylées au survol (hover)
# - DOB a un titre explicite et une infobulle mise en évidence
# - Calculs : DL (simulation déterministe), EXP (pour < 70 ans), DD (simulation)
# - Export JSON
# ---------------------------

# ---------------------------
# Fonctions utilitaires
# ---------------------------

def calc_expiration(dob: date, issue_date: date) -> date:
    """Pour conducteurs < 70 ans : expiration = anniversaire du titulaire, 5 ans après l'année d'émission."""
    exp_year = issue_date.year + 5
    try:
        return date(exp_year, dob.month, dob.day)
    except ValueError:
        # Cas 29 février -> 28 février si non bissextile
        return date(exp_year, 2, 28)

def calc_dl(last_name: str, dob: date) -> str:
    """
    Génération académique déterministe d'un numéro DL :
    - Lettre = initiale du nom de famille (majuscule) ou 'X' si absent
    - 7 chiffres = extraits d'un hash SHA1 de la DOB (YYYYMMDD), complétés par MD5 si nécessaire
    """
    if not last_name or not re.search(r'[A-Za-z]', last_name):
        letter = "X"
    else:
        letter = re.sub(r'[^A-Za-z]', '', last_name)[0].upper()

    dob_str = dob.strftime("%Y%m%d")
    h = hashlib.sha1(dob_str.encode()).hexdigest()
    digits = ''.join([c for c in h if c.isdigit()])
    if len(digits) < 7:
        extra = hashlib.md5(dob_str.encode()).hexdigest()
        digits += ''.join([c for c in extra if c.isdigit()])
    digits = (digits + "0" * 7)[:7]
    return f"{letter}{digits}"

def calc_dd(issue_date: date) -> str:
    """
    Génération simulée du Document Discriminator (DD) :
    - Préfixe : MMDDYYYY (date d'émission)
    - Suffixe : 6 hex chars issus d'un MD5 de la date d'émission
    """
    code = issue_date.strftime("%m%d%Y")
    suffix = hashlib.md5(code.encode()).hexdigest()[:6].upper()
    return f"{code}{suffix}"

def to_json_result(result: dict) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2)

def calculate_age(birth_date: date, ref_date: date) -> int:
    """Calcule l'âge au jour de référence (ref_date)."""
    return ref_date.year - birth_date.year - ((ref_date.month, ref_date.day) < (birth_date.month, birth_date.day))

# ---------------------------
# Tooltips (définitions brèves)
# ---------------------------

TOOLTIPS = {
    "LN": "Nom de famille — nom de famille du titulaire.",
    "FN": "Prénom — prénom du titulaire.",
    "DOB": "Date de naissance — format YYYY-MM-DD. Utilisée pour calculer l'âge et générer le DL simulé.",
    "ISS": "Date d'émission — date où le permis a été délivré.",
    "EXP": "Date d'expiration — pour <70 ans : anniversaire + 5 ans.",
    "DL": "Driver License — initiale du nom + 7 chiffres (simulation académique).",
    "DD": "Document Discriminator — code unique simulé basé sur ISS.",
    "SEX": "Sexe — M ou F (ou X).",
    "HGT": "Taille — ex. 5'-08''.",
    "WGT": "Poids — en livres (lb).",
    "HAIR": "Couleur des cheveux.",
    "EYES": "Couleur des yeux.",
    "CLASS": "Classe de permis — ex. C pour véhicule standard.",
    "RSTR": "Restrictions — ex. port de lunettes obligatoire.",
    "END": "Endorsements — autorisations spéciales."
}

def label_with_tooltip(key: str, label_text: str) -> str:
    """Retourne un fragment HTML pour un label avec tooltip stylé."""
    tip = html.escape(TOOLTIPS.get(key, ""))
    label_html = f'''
    <div class="label-tooltip">
      <span class="label-text" title="{tip}">{html.escape(label_text)}</span>
      <span class="tooltip-text" role="tooltip">{tip}</span>
    </div>
    '''
    return label_html

# ---------------------------
# CSS pour tooltips stylées (DOB mise en évidence)
# ---------------------------

TOOLTIP_CSS = """
<style>
.label-tooltip {
  position: relative;
  display: inline-block;
  margin-bottom: 6px;
}
.label-text {
  font-weight: 600;
  color: #0f172a;
  text-decoration: underline dotted;
  cursor: help;
  padding-right: 6px;
}
.tooltip-text {
  visibility: hidden;
  width: max-content;
  max-width: 360px;
  background-color: rgba(15,23,42,0.96);
  color: #fff;
  text-align: left;
  border-radius: 8px;
  padding: 10px 12px;
  position: absolute;
  z-index: 9999;
  bottom: 135%;
  left: 0;
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 0.14s ease, transform 0.14s ease, visibility 0.14s;
  box-shadow: 0 8px 24px rgba(2,6,23,0.25);
  font-size: 13px;
  line-height: 1.35;
}
.label-tooltip:hover .tooltip-text,
.label-tooltip:focus-within .tooltip-text {
  visibility: visible;
  opacity: 1;
  transform: translateY(0);
}
.tooltip-text::after {
  content: "";
  position: absolute;
  top: 100%;
  left: 14px;
  border-width: 7px;
  border-style: solid;
  border-color: rgba(15,23,42,0.96) transparent transparent transparent;
}

/* Spécifique : mettre la DOB en évidence (couleur et taille légèrement différente) */
.label-tooltip.dob .label-text {
  color: #0b5cff;
  font-size: 15px;
}
.label-tooltip.dob .tooltip-text {
  max-width: 420px;
  font-size: 14px;
  padding: 12px 14px;
  background-color: rgba(11,92,255,0.95);
  color: #ffffff;
  box-shadow: 0 10px 30px rgba(11,92,255,0.12);
}

/* Accessibilité : focus visible */
.label-text:focus {
  outline: 3px solid rgba(11,92,255,0.18);
  outline-offset: 2px;
  border-radius: 4px;
}
</style>
"""

# ---------------------------
# Interface Streamlit
# ---------------------------

st.set_page_config(page_title="Calcul DL California - Académique", layout="centered")
st.markdown(TOOLTIP_CSS, unsafe_allow_html=True)

st.title("Calcul académique des champs d'un permis de conduire Californie ( < 70 ans )")
st.caption("Survolez les labels pour voir une définition brève. Les numéros générés sont des simulations déterministes pour usage académique.")

# Deux colonnes pour le formulaire
col1, col2 = st.columns(2)

with col1:
    st.markdown(label_with_tooltip("LN", "Nom de famille (LN)"), unsafe_allow_html=True)
    ln = st.text_input("", value="Harms", placeholder="Ex: Harms")

    st.markdown(label_with_tooltip("FN", "Prénom (FN)"), unsafe_allow_html=True)
    fn = st.text_input("", value="Rosa", placeholder="Ex: Rosa")

    # DOB : titre explicite + infobulle mise en évidence
    dob_label_html = '''
    <div class="label-tooltip dob">
      <span class="label-text" title="Date de naissance — format YYYY-MM-DD. Utilisée pour calculer l'âge et générer le DL simulé.">Date de naissance (DOB, YYYY-MM-DD)</span>
      <span class="tooltip-text" role="tooltip">Date de naissance — format YYYY-MM-DD. Utilisée pour calculer l'âge et générer le DL simulé.</span>
    </div>
    '''
    st.markdown(dob_label_html, unsafe_allow_html=True)
    dob_str = st.text_input("Date de naissance (DOB, YYYY-MM-DD)", value="1990-12-31", placeholder="YYYY-MM-DD")

    st.markdown(label_with_tooltip("ISS", "Date d'émission (ISS, YYYY-MM-DD)"), unsafe_allow_html=True)
    iss_str = st.text_input("", value="2015-09-30", placeholder="YYYY-MM-DD")

with col2:
    st.markdown(label_with_tooltip("SEX", "Sexe (SEX)"), unsafe_allow_html=True)
    sex = st.selectbox("", options=["F", "M", "X"], index=0)

    st.markdown(label_with_tooltip("HGT", "Taille (HGT)"), unsafe_allow_html=True)
    hgt = st.text_input("", value="5'-08''", placeholder="Ex: 5'-08''")

    st.markdown(label_with_tooltip("WGT", "Poids (WGT)"), unsafe_allow_html=True)
    wgt = st.text_input("", value="175 lb", placeholder="Ex: 175 lb")

    st.markdown(label_with_tooltip("CLASS", "Classe (CLASS)"), unsafe_allow_html=True)
    pclass = st.text_input("", value="C", placeholder="Ex: C")

    st.markdown(label_with_tooltip("RSTR", "Restrictions (RSTR)"), unsafe_allow_html=True)
    rstr = st.text_input("", value="NONE", placeholder="Ex: NONE")

# Bouton calculer
if st.button("Calculer"):
    # Validation minimale des dates
    try:
        dob = datetime.strptime(dob_str.strip(), "%Y-%m-%d").date()
    except Exception:
        st.error("Format DOB invalide. Utilisez YYYY-MM-DD.")
        st.stop()

    try:
        iss = datetime.strptime(iss_str.strip(), "%Y-%m-%d").date()
    except Exception:
        st.error("Format ISS invalide. Utilisez YYYY-MM-DD.")
        st.stop()

    # Calcul âge au moment de l'émission et âge actuel
    age_at_issue = calculate_age(dob, iss)
    age_now = calculate_age(dob, date.today())

    # Vérification < 70 ans (conforme au périmètre demandé)
    if age_at_issue >= 70:
        st.warning("Attention : ce calcul est conçu pour les conducteurs de moins de 70 ans. Les règles changent pour >= 70 ans.")

    # Calculs
    dl = calc_dl(ln, dob)
    exp = calc_expiration(dob, iss)
    dd = calc_dd(iss)

    result = {
        "DL": dl,
        "EXP": exp.isoformat(),
        "ISS": iss.isoformat(),
        "DD": dd,
        "LN": ln,
        "FN": fn,
        "DOB": dob.isoformat(),
        "AGE_AT_ISSUE": age_at_issue,
        "AGE_NOW": age_now,
        "SEX": sex,
        "HGT": hgt,
        "WGT": wgt,
        "HAIR": "",
        "EYES": "",
        "CLASS": pclass,
        "RSTR": rstr,
        "END": ""
    }

    st.subheader("Résultats simulés")
    st.write(f"**DL :** {dl}")
    st.write(f"**EXP :** {exp.isoformat()}")
    st.write(f"**ISS :** {iss.isoformat()}")
    st.write(f"**DD :** {dd}")
    st.write("---")
    st.write(f"**LN :** {ln}")
    st.write(f"**FN :** {fn}")
    st.write(f"**DOB :** {dob.isoformat()}  — **Âge maintenant :** {age_now} ans")
    st.write(f"**Âge au moment de l'émission :** {age_at_issue} ans")
    st.write(f"**SEX :** {sex}")
    st.write(f"**HGT :** {hgt}")
    st.write(f"**WGT :** {wgt}")
    st.write(f"**CLASS :** {pclass}")
    st.write(f"**RSTR :** {rstr}")

    # Export JSON
    st.download_button(
        label="Exporter résultats (JSON)",
        data=to_json_result(result),
        file_name=f"dl_simulation_{dl}.json",
        mime="application/json"
    )

    st.subheader("JSON (simulation)")
    st.code(to_json_result(result), language="json")

# Footer explicatif (court)
st.markdown(
    """
    **Notes**  
    - Les valeurs générées sont des simulations déterministes pour usage académique uniquement.
    """,
    unsafe_allow_html=True
)
