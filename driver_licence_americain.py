import streamlit as st
import html
import re
import json
from datetime import date, datetime, timedelta
import hashlib

# ---------------------------
# app.py - Version finale complète
# - Aucun champ d'entrée pour EXP (date d'expiration) : EXP est calculée automatiquement
# - EXP = anniversaire du titulaire, 5 ans après l'année d'émission (anniversary + 5 years)
# - DOB ≤ today - 16 years (âge ≥ 16)
# - ISS < today (strictement antérieure)
# - EXP peut tomber dans l'année courante, mais doit être strictement > today (jour courant KO)
# - Validation complète, infobulles, export JSON
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
    """DL simulé : initiale du nom + 7 chiffres dérivés de la DOB (déterministe)."""
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
# Tooltips / UI helpers
# ---------------------------

TOOLTIPS = {
    "LN": "Nom de famille — ex. Dupont.",
    "FN": "Prénom — ex. Marie.",
    "SEX": "Sexe — M, F ou X.",
    "HGT": "Taille — format libre, ex. 5'-08''.",
    "WGT": "Poids — ex. 175 lb.",
    "HAIR": "Cheveux — ex. BRN.",
    "EYES": "Yeux — ex. BRO.",
    "DOB": "Date de naissance — format YYYY-MM-DD. Doit être ≤ aujourd'hui - 16 ans.",
    "ISS": "Date d'émission — format YYYY-MM-DD. Doit être antérieure à aujourd'hui.",
    "EXP": "Date d'expiration (calculée) — anniversaire + 5 ans ; doit être strictement après aujourd'hui.",
    "CLASS": "Classe de permis — ex. C.",
    "RSTR": "Restrictions — ex. NONE, GLASSES.",
    "END": "Endorsements — autorisations spéciales."
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
  font-size: 13px; line-height: 1.3; max-width: 420px;
}
.label-tooltip:hover .tooltip-text, .label-tooltip:focus-within .tooltip-text { visibility: visible; opacity: 1; transform: translateY(0); }
.tooltip-text::after { content: ""; position: absolute; top: 100%; left: 12px; border-width: 6px; border-style: solid; border-color: rgba(15,23,42,0.96) transparent transparent transparent; }
.label-tooltip.dob .label-text { color: #0b5cff; font-size: 15px; }
.label-tooltip.dob .tooltip-text { background-color: rgba(11,92,255,0.95); box-shadow: 0 10px 30px rgba(11,92,255,0.12); }
</style>
"""

# ---------------------------
# Interface Streamlit
# ---------------------------

st.set_page_config(page_title="Calcul DL - Final (EXP calculée)", layout="centered")
st.markdown(TOOLTIP_CSS, unsafe_allow_html=True)

st.title("Calcul académique des champs d'un permis de conduire Californie")
st.caption("DOB ≤ aujourd'hui - 16 ans ; ISS < aujourd'hui ; EXP calculée = anniversaire + 5 ans (doit être > aujourd'hui).")

today = date.today()
min_dob_allowed = safe_subtract_years(today, 120)
max_dob_allowed = safe_subtract_years(today, 16)   # DOB ≤ today - 16 years
max_iss_allowed = today - timedelta(days=1)        # ISS < today (strictement antérieure)

# Formulaire
col1, col2 = st.columns(2)

with col1:
    st.markdown(label_with_tooltip("LN", "Nom de famille (LN)"), unsafe_allow_html=True)
    ln = st.text_input("", value="Harms", placeholder="Ex: Harms")

    st.markdown(label_with_tooltip("FN", "Prénom (FN)"), unsafe_allow_html=True)
    fn = st.text_input("", value="Rosa", placeholder="Ex: Rosa")

    st.markdown(label_with_tooltip("DOB", "Date de naissance (DOB, YYYY-MM-DD)"), unsafe_allow_html=True)
    dob = st.date_input("", value=date(1990, 12, 31), min_value=min_dob_allowed, max_value=max_dob_allowed, key="dob_input")

    st.markdown(label_with_tooltip("ISS", "Date d'émission (ISS, YYYY-MM-DD)"), unsafe_allow_html=True)
    iss = st.date_input("", value=date(2015, 9, 30), max_value=max_iss_allowed, key="iss_input")

with col2:
    st.markdown(label_with_tooltip("SEX", "Sexe (SEX)"), unsafe_allow_html=True)
    sex = st.selectbox("", options=["F", "M", "X"], index=0)

    st.markdown(label_with_tooltip("HGT", "Taille (HGT)"), unsafe_allow_html=True)
    hgt = st.text_input("", value="5'-08''", placeholder="Ex: 5'-08''")

    st.markdown(label_with_tooltip("WGT", "Poids (WGT)"), unsafe_allow_html=True)
    wgt = st.text_input("", value="175 lb", placeholder="Ex: 175 lb")

    st.markdown(label_with_tooltip("HAIR", "Cheveux (HAIR)"), unsafe_allow_html=True)
    hair = st.text_input("", value="BRN", placeholder="Ex: BRN")

    st.markdown(label_with_tooltip("EYES", "Yeux (EYES)"), unsafe_allow_html=True)
    eyes = st.text_input("", value="BRO", placeholder="Ex: BRO")

    st.markdown(label_with_tooltip("CLASS", "Classe (CLASS)"), unsafe_allow_html=True)
    pclass = st.text_input("", value="C", placeholder="Ex: C")

    st.markdown(label_with_tooltip("RSTR", "Restrictions (RSTR)"), unsafe_allow_html=True)
    rstr = st.text_input("", value="NONE", placeholder="Ex: NONE")

    st.markdown(label_with_tooltip("END", "Endorsements (END)"), unsafe_allow_html=True)
    end = st.text_input("", value="", placeholder="Ex: MOTORCYCLE")

# Bouton calculer
if st.button("Calculer"):
    errors = []

    # Vérifications de base
    if not ln.strip():
        errors.append("Le nom de famille (LN) est obligatoire.")
    if not fn.strip():
        errors.append("Le prénom (FN) est obligatoire.")
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

    # ISS doit être postérieure à DOB (logique)
    if isinstance(dob, date) and isinstance(iss, date) and iss <= dob:
        errors.append("La date d'émission doit être postérieure à la date de naissance.")

    # Calcul EXP (basée sur l'anniversaire + 5 ans)
    exp = None
    if isinstance(dob, date) and isinstance(iss, date):
        exp = calc_expiration(dob, iss)
        # Règle stricte : EXP doit être strictement après today
        if exp <= today:
            errors.append(f"La date d'expiration calculée ({exp.isoformat()}) n'est pas valide. Elle doit être strictement après {today.isoformat()}.")

    # Afficher erreurs si présentes
    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    # Génération des champs simulés
    dl = calc_dl(ln, dob)
    dd = calc_dd(iss)
    age_at_issue = calculate_age(dob, iss)
    age_now = calculate_age(dob, today)

    result = {
        "DL": dl,
        "EXP": exp.isoformat() if exp else None,
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
        "HAIR": hair,
        "EYES": eyes,
        "CLASS": pclass,
        "RSTR": rstr,
        "END": end
    }

    # Affichage résultats
    st.subheader("Résultats simulés")
    st.write(f"**DL :** {dl}")
    st.write(f"**EXP (calculée) :** {exp.isoformat()}  — (doit être strictement après {today.isoformat()})")
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
    st.write(f"**HAIR :** {hair}")
    st.write(f"**EYES :** {eyes}")
    st.write(f"**CLASS :** {pclass}")
    st.write(f"**RSTR :** {rstr}")
    st.write(f"**END :** {end}")

    # Export JSON
    st.download_button(
        label="Exporter résultats (JSON)",
        data=to_json_result(result),
        file_name=f"dl_simulation_{dl}.json",
        mime="application/json"
    )

    st.subheader("JSON (simulation)")
    st.code(to_json_result(result), language="json")
