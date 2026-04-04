import streamlit as st
import html
import re
import json
from datetime import date, datetime, timedelta
import hashlib

# ---------------------------
# app.py - Version finale avec contraintes strictes de date
# - DOB et ISS doivent être antérieurs à aujourd'hui
# - DOB doit être au moins 16 ans avant aujourd'hui (âge >= 16)
# - ISS doit être strictement antérieure à aujourd'hui
# - EXP (calculée) doit être strictement dans le futur (exp > today)
# - Les sélecteurs de date utilisent le calendrier (st.date_input) et l'affichage se fait en YYYY-MM-DD
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
    """Génération académique déterministe d'un numéro DL : Lettre + 7 chiffres dérivés de la DOB."""
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
    """Génération simulée du Document Discriminator (DD) : MMDDYYYY + 6 hex chars."""
    code = issue_date.strftime("%m%d%Y")
    suffix = hashlib.md5(code.encode()).hexdigest()[:6].upper()
    return f"{code}{suffix}"

def to_json_result(result: dict) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2)

def calculate_age(birth_date: date, ref_date: date) -> int:
    return ref_date.year - birth_date.year - ((ref_date.month, ref_date.day) < (birth_date.month, birth_date.day))

def safe_subtract_years(d: date, years: int) -> date:
    """Soustrait des années en gérant 29 février."""
    try:
        return date(d.year - years, d.month, d.day)
    except ValueError:
        # 29 février -> 28 février
        return date(d.year - years, 2, 28)

# ---------------------------
# Tooltips (définitions brèves)
# ---------------------------

TOOLTIPS = {
    "LN": "Nom de famille — nom de famille du titulaire.",
    "FN": "Prénom — prénom du titulaire.",
    "DOB": "Date de naissance — format YYYY-MM-DD. Doit être ≤ (au plus) aujourd'hui - 16 ans.",
    "ISS": "Date d'émission — date où le permis a été délivré. Doit être antérieure à aujourd'hui.",
    "EXP": "Date d'expiration — pour <70 ans : anniversaire + 5 ans (doit être dans le futur).",
    "DL": "Driver License — initiale du nom + 7 chiffres (simulation académique).",
    "DD": "Document Discriminator — code unique simulé basé sur ISS.",
    "SEX": "Sexe — M ou F (ou X).",
    "HGT": "Taille — ex. 5'-08''.",
    "WGT": "Poids — en livres (lb).",
    "CLASS": "Classe de permis — ex. C pour véhicule standard.",
    "RSTR": "Restrictions — ex. port de lunettes obligatoire."
}

def label_with_tooltip(key: str, label_text: str) -> str:
    tip = html.escape(TOOLTIPS.get(key, ""))
    label_html = f'''
    <div class="label-tooltip">
      <span class="label-text" title="{tip}">{html.escape(label_text)}</span>
      <span class="tooltip-text" role="tooltip">{tip}</span>
    </div>
    '''
    return label_html

TOOLTIP_CSS = """
<style>
.label-tooltip { position: relative; display: inline-block; margin-bottom: 6px; }
.label-text { font-weight: 600; color: #0f172a; text-decoration: underline dotted; cursor: help; padding-right: 6px; }
.tooltip-text {
  visibility: hidden; width: max-content; max-width: 360px; background-color: rgba(15,23,42,0.96); color: #fff;
  text-align: left; border-radius: 8px; padding: 10px 12px; position: absolute; z-index: 9999; bottom: 135%; left: 0;
  opacity: 0; transform: translateY(8px); transition: opacity 0.14s ease, transform 0.14s ease, visibility 0.14s;
  box-shadow: 0 8px 24px rgba(2,6,23,0.25); font-size: 13px; line-height: 1.35;
}
.label-tooltip:hover .tooltip-text, .label-tooltip:focus-within .tooltip-text { visibility: visible; opacity: 1; transform: translateY(0); }
.tooltip-text::after { content: ""; position: absolute; top: 100%; left: 14px; border-width: 7px; border-style: solid; border-color: rgba(15,23,42,0.96) transparent transparent transparent; }
.label-tooltip.dob .label-text { color: #0b5cff; font-size: 15px; }
.label-tooltip.dob .tooltip-text { max-width: 420px; font-size: 14px; padding: 12px 14px; background-color: rgba(11,92,255,0.95); color: #ffffff; box-shadow: 0 10px 30px rgba(11,92,255,0.12); }
.label-text:focus { outline: 3px solid rgba(11,92,255,0.18); outline-offset: 2px; border-radius: 4px; }
</style>
"""

# ---------------------------
# Interface Streamlit
# ---------------------------

st.set_page_config(page_title="Calcul DL - Contraintes de date", layout="centered")
st.markdown(TOOLTIP_CSS, unsafe_allow_html=True)

st.title("Calcul DL California — contraintes de date")
st.caption("Cliquez sur la date pour ouvrir le calendrier. Les formats affichés sont YYYY-MM-DD.")

today = date.today()
min_dob_allowed = safe_subtract_years(today, 120)  # limite raisonnable pour la saisie
max_dob_allowed = safe_subtract_years(today, 16)   # DOB doit être ≤ today - 16 ans
max_iss_allowed = today - timedelta(days=1)        # ISS doit être strictement antérieure à aujourd'hui

col1, col2 = st.columns(2)

with col1:
    st.markdown(label_with_tooltip("LN", "Nom de famille (LN)"), unsafe_allow_html=True)
    ln = st.text_input("", value="Harms", placeholder="Ex: Harms")

    st.markdown(label_with_tooltip("FN", "Prénom (FN)"), unsafe_allow_html=True)
    fn = st.text_input("", value="Rosa", placeholder="Ex: Rosa")

    # DOB : date_input avec calendrier ; max_value = today - 16 years (âge >= 16)
    st.markdown('''
    <div class="label-tooltip dob">
      <span class="label-text" title="Date de naissance — format YYYY-MM-DD. Doit être ≤ aujourd'hui - 16 ans.">Date de naissance (DOB, YYYY-MM-DD)</span>
      <span class="tooltip-text" role="tooltip">Date de naissance — format YYYY-MM-DD. Doit être ≤ aujourd'hui - 16 ans.</span>
    </div>
    ''', unsafe_allow_html=True)
    dob = st.date_input("", value=date(1990, 12, 31), min_value=min_dob_allowed, max_value=max_dob_allowed, key="dob_input")

    st.markdown(label_with_tooltip("ISS", "Date d'émission (ISS, YYYY-MM-DD)"), unsafe_allow_html=True)
    # ISS : date_input avec calendrier ; max_value = today - 1 day (strictement antérieure à aujourd'hui)
    iss = st.date_input("", value=date(2015, 9, 30), max_value=max_iss_allowed, key="iss_input")

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
    errors = []

    # Champs obligatoires
    if not ln.strip():
        errors.append("Le nom de famille (LN) est obligatoire.")
    if not fn.strip():
        errors.append("Le prénom (FN) est obligatoire.")
    if not isinstance(dob, date):
        errors.append("Date de naissance invalide.")
    if not isinstance(iss, date):
        errors.append("Date d'émission invalide.")

    # DOB doit être ≤ today - 16 ans
    if isinstance(dob, date):
        if dob > max_dob_allowed:
            errors.append(f"La date de naissance doit être au plus le {max_dob_allowed.isoformat()} (âge ≥ 16 ans).")

    # ISS doit être strictement antérieure à aujourd'hui
    if isinstance(iss, date):
        if iss >= today:
            errors.append("La date d'émission doit être antérieure à aujourd'hui.")

    # ISS ne peut être antérieure à DOB (logique)
    if isinstance(dob, date) and isinstance(iss, date):
        if iss <= dob:
            errors.append("La date d'émission doit être postérieure à la date de naissance.")

    # Calcul EXP et vérification qu'elle soit strictement dans le futur
    if isinstance(dob, date) and isinstance(iss, date):
        exp = calc_expiration(dob, iss)
        if exp <= today:
            errors.append("La date d'expiration calculée n'est pas dans le futur. Vérifiez la date d'émission et la date de naissance.")
    else:
        exp = None

    # Afficher erreurs si présentes
    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    # Si tout est OK, générer les autres champs simulés
    dl = calc_dl(ln, dob)
    dd = calc_dd(iss)
    age_at_issue = calculate_age(dob, iss)
    age_now = calculate_age(dob, today)

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
        "CLASS": pclass,
        "RSTR": rstr
    }

    st.subheader("Résultats simulés")
    st.write(f"**DL :** {dl}")
    st.write(f"**EXP :** {exp.isoformat()}  (doit être strictement dans le futur)")
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

    st.download_button(
        label="Exporter résultats (JSON)",
        data=to_json_result(result),
        file_name=f"dl_simulation_{dl}.json",
        mime="application/json"
    )

    st.subheader("JSON (simulation)")
    st.code(to_json_result(result), language="json")
