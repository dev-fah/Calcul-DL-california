import streamlit as st
import html
import re
import json
from datetime import date, datetime
import hashlib

# ---------------------------
# Configuration et explications
# ---------------------------
# Ce fichier est une application Streamlit autonome.
# - Les tooltips sont implémentées en HTML/CSS et affichées au survol (hover).
# - DL (simulation) : initiale du nom (majuscule) + 7 chiffres déterministes extraits d'un hash SHA1 de la DOB (YYYYMMDD).
# - EXP (pour < 70 ans) : date d'anniversaire du titulaire, 5 ans après l'année d'émission.
# - DD (simulation) : MMDDYYYY (ISS) + suffixe 6 hex chars issu d'un MD5 de la date d'émission.
# Les numéros générés sont des simulations déterministes pour usage académique uniquement.

# ---------------------------
# Fonctions utilitaires
# ---------------------------

def calc_expiration(dob: date, issue_date: date) -> date:
    """
    Pour conducteurs < 70 ans : expiration = anniversaire du titulaire,
    5 ans après l'année d'émission.
    """
    exp_year = issue_date.year + 5
    try:
        return date(exp_year, dob.month, dob.day)
    except ValueError:
        # Cas 29 février -> 28 février si non bissextile
        return date(exp_year, 2, 28)

def calc_dl(last_name: str, dob: date) -> str:
    """
    Génération académique et déterministe d'un numéro DL :
    - Lettre = initiale du nom de famille (majuscule)
    - 7 chiffres = extraits d'un hash SHA1 de la DOB formatée YYYYMMDD
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

# ---------------------------
# Tooltips (définitions brèves)
# ---------------------------

TOOLTIPS = {
    "LN": "Nom de famille — nom de famille du titulaire.",
    "FN": "Prénom — prénom du titulaire.",
    "DOB": "Date de naissance — format YYYY-MM-DD.",
    "ISS": "Date d'émission — date où le permis a été délivré.",
    "EXP": "Date d'expiration — pour <70 ans : anniversaire + 5 ans.",
    "DL": "Driver License — initiale du nom + 7 chiffres (simulation).",
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
    """
    Retourne un fragment HTML pour un label avec tooltip stylé.
    Utilise data-tooltip pour le texte et CSS pour l'effet hover.
    """
    tip = html.escape(TOOLTIPS.get(key, ""))
    label_html = f'''
    <div class="label-tooltip">
      <span class="label-text">{html.escape(label_text)}</span>
      <span class="tooltip-text">{tip}</span>
    </div>
    '''
    return label_html

# ---------------------------
# CSS pour tooltips stylées
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
}
.tooltip-text {
  visibility: hidden;
  width: max-content;
  max-width: 320px;
  background-color: rgba(15,23,42,0.95);
  color: #fff;
  text-align: left;
  border-radius: 6px;
  padding: 8px 10px;
  position: absolute;
  z-index: 9999;
  bottom: 125%;
  left: 0;
  opacity: 0;
  transform: translateY(6px);
  transition: opacity 0.18s ease, transform 0.18s ease, visibility 0.18s;
  box-shadow: 0 6px 18px rgba(2,6,23,0.2);
  font-size: 13px;
  line-height: 1.3;
}
.label-tooltip:hover .tooltip-text {
  visibility: visible;
  opacity: 1;
  transform: translateY(0);
}
.tooltip-text::after {
  content: "";
  position: absolute;
  top: 100%;
  left: 12px;
  margin-left: -5px;
  border-width: 6px;
  border-style: solid;
  border-color: rgba(15,23,42,0.95) transparent transparent transparent;
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

    st.markdown(label_with_tooltip("DOB", "Date de naissance (DOB, YYYY-MM-DD)"), unsafe_allow_html=True)
    dob_str = st.text_input("", value="1990-12-31", placeholder="YYYY-MM-DD")

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

    # Calcul âge au moment de l'émission
    age_at_issue = iss.year - dob.year - ((iss.month, iss.day) < (dob.month, dob.day))
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
    st.write(f"**DOB :** {dob.isoformat()}")
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

# Footer explicatif
st.markdown(
    """
    **Notes**  
    - Les numéros générés ici sont des **simulations déterministes** pour usage académique uniquement.  
    - Format observé pour les DL californiens : souvent `1 lettre + 7 chiffres`. Ici la lettre = initiale du nom.  
    - Le Document Discriminator (DD) réel est interne au DMV ; nous simulons un code traçable basé sur la date d'émission.
    """,
    unsafe_allow_html=True
)
