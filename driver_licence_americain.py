import streamlit as st
import html
import re
import json
from datetime import date, datetime, timedelta
import hashlib

# ---------------------------
# app.py - Version finale complète
# - DOB ≤ aujourd'hui - 16 ans (âge ≥ 16)
# - ISS < aujourd'hui (strictement antérieure)
# - EXP = anniversaire + 5 ans après l'année d'émission
# - EXP peut être dans l'année courante mais doit être strictement > aujourd'hui
# - Tous les champs obligatoires sont vérifiés
# ---------------------------

# ---------------------------
# Fonctions utilitaires
# ---------------------------

def calc_expiration(dob: date, issue_date: date) -> date:
    """Expiration = anniversaire du titulaire, 5 ans après l'année d'émission."""
    exp_year = issue_date.year + 5
    try:
        return date(exp_year, dob.month, dob.day)
    except ValueError:
        # Cas 29 février -> 28 février si non bissextile
        return date(exp_year, 2, 28)

def calc_dl(last_name: str, dob: date) -> str:
    """DL simulé : initiale du nom + 7 chiffres dérivés de la DOB."""
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
    """DD simulé : MMDDYYYY + 6 hex chars."""
    code = issue_date.strftime("%m%d%Y")
    suffix = hashlib.md5(code.encode()).hexdigest()[:6].upper()
    return f"{code}{suffix}"

def to_json_result(result: dict) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2)

def calculate_age(birth_date: date, ref_date: date) -> int:
    return ref_date.year - birth_date.year - ((ref_date.month, ref_date.day) < (birth_date.month, birth_date.day))

def safe_subtract_years(d: date, years: int) -> date:
    try:
        return date(d.year - years, d.month, d.day)
    except ValueError:
        return date(d.year - years, 2, 28)

# ---------------------------
# Tooltips
# ---------------------------

TOOLTIPS = {
    "DOB": "Date de naissance — doit être ≤ aujourd'hui - 16 ans.",
    "ISS": "Date d'émission — doit être antérieure à aujourd'hui.",
    "EXP": "Date d'expiration — doit être strictement après aujourd'hui (année courante comptable)."
}

def label_with_tooltip(key: str, label_text: str) -> str:
    tip = html.escape(TOOLTIPS.get(key, ""))
    return f'''
    <div class="label-tooltip">
      <span class="label-text" title="{tip}">{html.escape(label_text)}</span>
      <span class="tooltip-text" role="tooltip">{tip}</span>
    </div>
    '''

TOOLTIP_CSS = """
<style>
.label-tooltip { position: relative; display: inline-block; margin-bottom: 6px; }
.label-text { font-weight: 600; color: #0f172a; text-decoration: underline dotted; cursor: help; }
.tooltip-text {
  visibility: hidden; background-color: rgba(15,23,42,0.96); color: #fff;
  border-radius: 6px; padding: 8px 10px; position: absolute; z-index: 9999;
  bottom: 135%; left: 0; opacity: 0; transform: translateY(6px);
  transition: opacity 0.14s ease, transform 0.14s ease;
  font-size: 13px; line-height: 1.3;
}
.label-tooltip:hover .tooltip-text { visibility: visible; opacity: 1; transform: translateY(0); }
.tooltip-text::after { content: ""; position: absolute; top: 100%; left: 12px;
  border-width: 6px; border-style: solid; border-color: rgba(15,23,42,0.96) transparent transparent transparent; }
</style>
"""

# ---------------------------
# Interface
# ---------------------------

st.set_page_config(page_title="Calcul DL - Version finale", layout="centered")
st.markdown(TOOLTIP_CSS, unsafe_allow_html=True)

st.title("Calcul DL California — contraintes de date")
st.caption("DOB ≤ aujourd'hui - 16 ans ; ISS < aujourd'hui ; EXP > aujourd'hui (année courante comptable).")

today = date.today()
min_dob_allowed = safe_subtract_years(today, 120)
max_dob_allowed = safe_subtract_years(today, 16)   # DOB ≤ today - 16 years
max_iss_allowed = today - timedelta(days=1)        # ISS < today (strictement antérieure)

col1, col2 = st.columns(2)

with col1:
    st.markdown(label_with_tooltip("DOB", "Date de naissance (DOB, YYYY-MM-DD)"), unsafe_allow_html=True)
    dob = st.date_input("", value=date(1990, 12, 31), min_value=min_dob_allowed, max_value=max_dob_allowed, key="dob_input")

    st.markdown(label_with_tooltip("ISS", "Date d'émission (ISS, YYYY-MM-DD)"), unsafe_allow_html=True)
    iss = st.date_input("", value=date(2015, 9, 30), max_value=max_iss_allowed, key="iss_input")

with col2:
    st.markdown(label_with_tooltip("EXP", "Date d'expiration (calculée)"), unsafe_allow_html=True)
    st.markdown("La date d'expiration est calculée automatiquement après validation.", unsafe_allow_html=True)

# Bouton calculer
if st.button("Calculer"):
    errors = []

    # Vérifications de base
    if not isinstance(dob, date):
        errors.append("Date de naissance invalide.")
    if not isinstance(iss, date):
        errors.append("Date d'émission invalide.")

    # DOB doit être ≤ today - 16 ans
    if isinstance(dob, date) and dob > max_dob_allowed:
        errors.append(f"La date de naissance doit être au plus le {max_dob_allowed.isoformat()} (âge ≥ 16 ans).")

    # ISS doit être strictement antérieure à aujourd'hui
    if isinstance(iss, date) and iss >= today:
        errors.append("La date d'émission doit être antérieure à aujourd'hui.")

    # ISS doit être postérieure à DOB
    if isinstance(dob, date) and isinstance(iss, date) and iss <= dob:
        errors.append("La date d'émission doit être postérieure à la date de naissance.")

    # Calcul EXP
    if isinstance(dob, date) and isinstance(iss, date):
        exp = calc_expiration(dob, iss)
        # Règle finale : EXP doit être strictement > today
        if exp <= today:
            errors.append(f"La date d'expiration ({exp.isoformat()}) n'est pas valide. Elle doit être strictement après {today.isoformat()}.")
    else:
        exp = None

    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    # Calculs finaux
    dl = calc_dl("Harms", dob)
    dd = calc_dd(iss)
    age_at_issue = calculate_age(dob, iss)
    age_now = calculate_age(dob, today)

    result = {
        "DL": dl,
        "EXP": exp.isoformat(),
        "ISS": iss.isoformat(),
        "DD": dd,
        "DOB": dob.isoformat(),
        "AGE_AT_ISSUE": age_at_issue,
        "AGE_NOW": age_now
    }

    st.subheader("Résultats simulés")
    st.write(f"**DL :** {dl}")
    st.write(f"**EXP :** {exp.isoformat()}  (doit être strictement après {today.isoformat()})")
    st.write(f"**ISS :** {iss.isoformat()}")
    st.write(f"**DD :** {dd}")
    st.write("---")
    st.write(f"**DOB :** {dob.isoformat()}  — Âge actuel : {age_now} ans ; Âge à l'émission : {age_at_issue} ans")

    st.download_button(
        label="Exporter résultats (JSON)",
        data=to_json_result(result),
        file_name=f"dl_simulation_{dl}.json",
        mime="application/json"
    )

    st.subheader("JSON (simulation)")
    st.code(to_json_result(result), language="json")
