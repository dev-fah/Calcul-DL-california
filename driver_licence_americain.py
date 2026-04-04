import streamlit as st
import html
import re
import json
from datetime import date, datetime, timedelta
import hashlib

# ---------------------------
# app.py - Version finale complète
# - Tooltips, validation DOB/ISS/EXP
# - Field Office selector
# - DD = ISS_MMDDYYYY - FO_CODE - EXP_YY - SEC (SEC from SHA-256, last 4/8 chars)
# - Export JSON
# ---------------------------

# ---------- Utilitaires ----------
def calc_expiration(dob: date, issue_date: date) -> date:
    """Expiration = anniversaire du titulaire, 5 ans après l'année d'émission."""
    exp_year = issue_date.year + 5
    try:
        return date(exp_year, dob.month, dob.day)
    except ValueError:
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

def calc_dd(issue_date: date, exp_date: date, office_code: str, length: int = 8) -> str:
    """
    DD simulé : [ISS_MMDDYYYY]-[FO_CODE]-[EXP_YY]-[SEC]
    - SEC = derniers caractères d'un SHA-256 (length = 4 ou 8)
    """
    if length not in (4, 8):
        raise ValueError("length must be 4 or 8")
    iss_str = issue_date.strftime("%m%d%Y")
    exp_yy = exp_date.strftime("%y")
    base_str = iss_str + office_code + exp_yy
    hash_val = hashlib.sha256(base_str.encode()).hexdigest().upper()
    sec = hash_val[-length:]
    return f"{iss_str}-{office_code}-{exp_yy}-{sec}"

def to_json_result(result: dict) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2)

def calculate_age(birth_date: date, ref_date: date) -> int:
    return ref_date.year - birth_date.year - ((ref_date.month, ref_date.day) < (birth_date.month, birth_date.day))

def safe_subtract_years(d: date, years: int) -> date:
    try:
        return date(d.year - years, d.month, d.day)
    except ValueError:
        return date(d.year - years, 2, 28)

# ---------- UI helpers ----------
TOOLTIPS = {
    "LN": "Nom de famille — ex. Dupont.",
    "FN": "Prénom — ex. Marie.",
    "SEX": "Sexe — M, F ou X.",
    "DOB": "Date de naissance — format YYYY-MM-DD. Doit être ≤ aujourd'hui - 16 ans.",
    "ISS": "Date d'émission — format YYYY-MM-DD. Doit être antérieure à aujourd'hui.",
    "EXP": "Date d'expiration (calculée) — anniversaire + 5 ans ; doit être strictement après aujourd'hui.",
    "FO": "Code du bureau DMV — ex. 509 (Pasadena)."
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

# ---------- Config UI ----------
st.set_page_config(page_title="Calcul DL + DD (final)", layout="centered")
st.markdown(TOOLTIP_CSS, unsafe_allow_html=True)

st.title("Calcul académique des champs d'un permis de conduire Californie")
st.caption("DOB ≤ aujourd'hui - 16 ans ; ISS < aujourd'hui ; EXP = anniversaire + 5 ans ; DD = ISS+FO+EXP+SEC (SHA-256).")

today = date.today()
min_dob_allowed = safe_subtract_years(today, 120)
max_dob_allowed = safe_subtract_years(today, 16)
max_iss_allowed = today - timedelta(days=1)

# ---------- Field Office codes ----------
office_codes = {
    "Pasadena": "509",
    "Los Angeles (Hope St)": "502",
    "San Francisco": "503",
    "San Diego": "501",
    "Sacramento": "500",
    "San Jose": "516",
    "Oakland (Claremont Ave)": "504",
    "Santa Monica": "548",
    "Hollywood": "661",
    "Glendale": "628",
    "Culver City": "611",
    "Long Beach": "507"
}

# Security length choice (4 or 8)
security_length = st.sidebar.selectbox("Longueur séquence de sécurité (SEC)", options=[8, 4], index=0)

# ---------- Formulaire ----------
col1, col2 = st.columns(2)

with col1:
    st.markdown(label_with_tooltip("LN", "Nom de famille (LN)"), unsafe_allow_html=True)
    ln = st.text_input("", value="Harms", placeholder="Ex: Harms")

    st.markdown(label_with_tooltip("FN", "Prénom (FN)"), unsafe_allow_html=True)
    fn = st.text_input("", value="Rosa", placeholder="Ex: Rosa")

    st.markdown(label_with_tooltip("DOB", "Date de naissance (DOB, YYYY-MM-DD)"), unsafe_allow_html=True)
    dob = st.date_input("", value=date(1990, 12, 31), min_value=min_dob_allowed, max_value=max_dob_allowed)

    st.markdown(label_with_tooltip("ISS", "Date d'émission (ISS, YYYY-MM-DD)"), unsafe_allow_html=True)
    iss = st.date_input("", value=date(2015, 9, 30), max_value=max_iss_allowed)

    st.markdown(label_with_tooltip("FO", "Code du bureau DMV"), unsafe_allow_html=True)
    office = st.selectbox("", options=list(office_codes.keys()))

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

# ---------- Calcul ----------
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

    # DOB <= today - 16 ans
    if isinstance(dob, date) and dob > max_dob_allowed:
        errors.append(f"La date de naissance doit être au plus le {max_dob_allowed.isoformat()} (âge ≥ 16 ans).")

    # ISS < today
    if isinstance(iss, date) and iss >= today:
        errors.append("La date d'émission doit être antérieure à aujourd'hui.")

    # ISS > DOB
    if isinstance(dob, date) and isinstance(iss, date) and iss <= dob:
        errors.append("La date d'émission doit être postérieure à la date de naissance.")

    # Calcul EXP
    exp = None
    if isinstance(dob, date) and isinstance(iss, date):
        exp = calc_expiration(dob, iss)
        if exp <= today:
            errors.append(f"La date d'expiration calculée ({exp.isoformat()}) n'est pas valide. Elle doit être strictement après {today.isoformat()}.")

    # Afficher erreurs
    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    # Génération DL et DD
    dl = calc_dl(ln, dob)
    office_code = office_codes[office]
    dd = calc_dd(iss, exp, office_code, length=security_length)

    # --- Vérification d'unicité (placeholder) ---
    # Ici, tu dois vérifier dans ta base si le DD existe déjà pour éviter les collisions.
    # Exemple (pseudo) :
    # if db.exists({"DD": dd}):
    #     st.error("Collision : DD déjà présent dans la base. Réessayez ou changez le FO_CODE.")
    #     st.stop()
    # (implémentation réelle dépend de ta base de données)

    age_at_issue = calculate_age(dob, iss)
    age_now = calculate_age(dob, today)

    result = {
        "DL": dl,
        "DD": dd,
        "EXP": exp.isoformat(),
        "ISS": iss.isoformat(),
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
        "END": end,
        "OFFICE": office,
        "OFFICE_CODE": office_code,
        "SEC_LENGTH": security_length
    }

    # Affichage
    st.subheader("Résultats simulés")
    st.write(f"**DL :** {dl}")
    st.write(f"**DD :** {dd}")
    st.write(f"**EXP :** {exp.isoformat()}  (doit être strictement après {today.isoformat()})")
    st.write(f"**ISS :** {iss.isoformat()}")
    st.write(f"**Office :** {office} ({office_code})")
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

    st.download_button(
        label="Exporter résultats (JSON)",
        data=to_json_result(result),
        file_name=f"dl_simulation_{dl}.json",
        mime="application/json"
    )

    st.subheader("JSON (simulation)")
    st.code(to_json_result(result), language="json")
