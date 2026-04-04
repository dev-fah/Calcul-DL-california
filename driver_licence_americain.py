import streamlit as st
import html
import re
import json
from datetime import date, datetime, timedelta
import hashlib

# ---------------------------
# Fonctions utilitaires
# ---------------------------

def calc_expiration(dob: date, issue_date: date) -> date:
    """Expiration = anniversaire du titulaire, 5 ans après l'année d'émission."""
    exp_year = issue_date.year + 5
    try:
        return date(exp_year, dob.month, dob.day)
    except ValueError:
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

def calc_dd(issue_date: date, exp_date: date, office_code: str, length: int = 8) -> str:
    """
    DD simulé : [ISS_MMDDYYYY]-[FO_CODE]-[EXP_YY]-[SEC]
    - SEC = derniers caractères d'un SHA-256
    """
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

# ---------------------------
# Tooltips
# ---------------------------

TOOLTIPS = {
    "LN": "Nom de famille — ex. Dupont.",
    "FN": "Prénom — ex. Marie.",
    "SEX": "Sexe — M, F ou X.",
    "DOB": "Date de naissance — doit être ≤ aujourd'hui - 16 ans.",
    "ISS": "Date d'émission — doit être antérieure à aujourd'hui.",
    "EXP": "Date d'expiration — calculée automatiquement (anniversaire + 5 ans).",
    "FO": "Code du bureau DMV — ex. 509 (Pasadena).",
    "CLASS": "Classe de permis — ex. C.",
    "RSTR": "Restrictions — ex. NONE.",
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

# ---------------------------
# Interface
# ---------------------------

st.set_page_config(page_title="Calcul DL + DD", layout="centered")

st.title("Calcul académique des champs d'un permis de conduire Californie")
st.caption("DOB ≤ aujourd'hui - 16 ans ; ISS < aujourd'hui ; EXP = anniversaire + 5 ans ; DD basé sur ISS, FO_CODE, EXP, SHA-256.")

today = date.today()
min_dob_allowed = safe_subtract_years(today, 120)
max_dob_allowed = safe_subtract_years(today, 16)
max_iss_allowed = today - timedelta(days=1)

# Codes de bureau DMV
office_codes = {
    "Pasadena": "509",
    "Los Angeles (Hope St)": "502",
    "San Francisco": "503",
    "San Diego": "501",
    "Sacramento": "500",
    "San Jose": "516",
    "Oakland": "504",
    "Santa Monica": "548",
    "Hollywood": "661",
    "Glendale": "628",
    "Culver City": "611",
    "Long Beach": "507"
}

col1, col2 = st.columns(2)

with col1:
    st.markdown(label_with_tooltip("LN", "Nom de famille (LN)"), unsafe_allow_html=True)
    ln = st.text_input("", value="Harms")

    st.markdown(label_with_tooltip("FN", "Prénom (FN)"), unsafe_allow_html=True)
    fn = st.text_input("", value="Rosa")

    st.markdown(label_with_tooltip("DOB", "Date de naissance (DOB)"), unsafe_allow_html=True)
    dob = st.date_input("", value=date(1990, 12, 31), min_value=min_dob_allowed, max_value=max_dob_allowed)

    st.markdown(label_with_tooltip("ISS", "Date d'émission (ISS)"), unsafe_allow_html=True)
    iss = st.date_input("", value=date(2015, 9, 30), max_value=max_iss_allowed)

    st.markdown(label_with_tooltip("FO", "Code du bureau DMV"), unsafe_allow_html=True)
    office = st.selectbox("", options=list(office_codes.keys()))

with col2:
    st.markdown(label_with_tooltip("SEX", "Sexe (SEX)"), unsafe_allow_html=True)
    sex = st.selectbox("", options=["F", "M", "X"], index=0)

    hgt = st.text_input("Taille (HGT)", value="5'-08''")
    wgt = st.text_input("Poids (WGT)", value="175 lb")
    hair = st.text_input("Cheveux (HAIR)", value="BRN")
    eyes = st.text_input("Yeux (EYES)", value="BRO")
    pclass = st.text_input("Classe (CLASS)", value="C")
    rstr = st.text_input("Restrictions (RSTR)", value="NONE")
    end = st.text_input("Endorsements (END)", value="")

# Bouton calculer
if st.button("Calculer"):
    errors = []

    if dob > max_dob_allowed:
        errors.append("DOB invalide : doit être ≤ aujourd'hui - 16 ans.")
    if iss >= today:
        errors.append("ISS invalide : doit être antérieure à aujourd'hui.")
    if iss <= dob:
        errors.append("ISS invalide : doit être postérieure à DOB.")

    exp = calc_expiration(dob, iss)
    if exp <= today:
        errors.append(f"EXP invalide ({exp.isoformat()}) : doit être strictement après {today.isoformat()}.")

    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    dl = calc_dl(ln, dob)
    dd = calc_dd(iss, exp, office_codes[office], length=8)
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
        "OFFICE": office
    }

    st.subheader("Résultats simulés")
    st.write(f"**DL :** {dl}")
    st.write(f"**DD :** {dd}")
    st.write(f"**EXP :** {exp.isoformat()}")
    st.write(f"**ISS :** {iss.isoformat()}")
    st.write(f"**Office :** {office} ({office_codes[office]})")
    st.write("---")
    st.write(f"**LN :** {ln}")
   Voici la **version finale complète de ton `app.py`**, intégrant la logique du **Document Discriminator (DD)** avec :

- Champ **Field Office Code** (sélecteur avec les codes DMV connus).  
- DD construit à partir de :  
  - **Date d’émission (ISS)** → `MMDDYYYY`  
  - **Code bureau (FO_CODE)**  
  - **Année d’expiration (EXP)** → 2 derniers chiffres  
  - **Séquence de sécurité** → générée par **SHA‑256**, extraction des 8 derniers caractères.  

Prêt à copier‑coller :

```python
import streamlit as st
import html
import re
import json
from datetime import date, datetime, timedelta
import hashlib

# ---------------------------
# Fonctions utilitaires
# ---------------------------

def calc_expiration(dob: date, issue_date: date) -> date:
    exp_year = issue_date.year + 5
    try:
        return date(exp_year, dob.month, dob.day)
    except ValueError:
        return date(exp_year, 2, 28)

def calc_dl(last_name: str, dob: date) -> str:
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
    SEC = derniers caractères d'un SHA-256
    """
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

# ---------------------------
# Codes de bureau DMV
# ---------------------------

office_codes = {
    "Pasadena": "509",
    "Los Angeles (Hope St)": "502",
    "San Francisco": "503",
    "San Diego": "501",
    "Sacramento": "500",
    "San Jose": "516",
    "Oakland": "504",
    "Santa Monica": "548",
    "Hollywood": "661",
    "Glendale": "628",
    "Culver City": "611",
    "Long Beach": "507"
}

# ---------------------------
# Interface
# ---------------------------

st.set_page_config(page_title="Calcul DL + DD", layout="centered")

st.title("Calcul académique des champs d'un permis de conduire Californie")
st.caption("DOB ≤ aujourd'hui - 16 ans ; ISS < aujourd'hui ; EXP = anniversaire + 5 ans ; DD basé sur ISS, FO_CODE, EXP, SHA-256.")

today = date.today()
min_dob_allowed = safe_subtract_years(today, 120)
max_dob_allowed = safe_subtract_years(today, 16)
max_iss_allowed = today - timedelta(days=1)

col1, col2 = st.columns(2)

with col1:
    ln = st.text_input("Nom de famille (LN)", value="Harms")
    fn = st.text_input("Prénom (FN)", value="Rosa")
    dob = st.date_input("Date de naissance (DOB)", value=date(1990, 12, 31), min_value=min_dob_allowed, max_value=max_dob_allowed)
    iss = st.date_input("Date d'émission (ISS)", value=date(2015, 9, 30), max_value=max_iss_allowed)
    office = st.selectbox("Code du bureau DMV", options=list(office_codes.keys()))

with col2:
    sex = st.selectbox("Sexe (SEX)", options=["F", "M", "X"], index=0)
    hgt = st.text_input("Taille (HGT)", value="5'-08''")
    wgt = st.text_input("Poids (WGT)", value="175 lb")
    hair = st.text_input("Cheveux (HAIR)", value="BRN")
    eyes = st.text_input("Yeux (EYES)", value="BRO")
    pclass = st.text_input("Classe (CLASS)", value="C")
    rstr = st.text_input("Restrictions (RSTR)", value="NONE")
    end = st.text_input("Endorsements (END)", value="")

# Bouton calculer
if st.button("Calculer"):
    errors = []

    if dob > max_dob_allowed:
        errors.append("DOB invalide : doit être ≤ aujourd'hui - 16 ans.")
    if iss >= today:
        errors.append("ISS invalide : doit être antérieure à aujourd'hui.")
    if iss <= dob:
        errors.append("ISS invalide : doit être postérieure à DOB.")

    exp = calc_expiration(dob, iss)
    if exp <= today:
        errors.append(f"EXP invalide ({exp.isoformat()}) : doit être strictement après {today.isoformat()}.")

    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    dl = calc_dl(ln, dob)
    dd = calc_dd(iss, exp, office_codes[office], length=8)
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
        "OFFICE": office
    }

    st.subheader("Résultats simulés")
    st.write(f"**DL :** {dl}")
    st.write(f"**DD :** {dd}")
    st.write(f"**EXP :** {exp.isoformat()}")
    st.write(f"**ISS :** {iss.isoformat()}")
    st.write(f"**Office :** {office} ({office_codes[office]})")
    st.write("---")
    st.write(f"**LN :** {ln}")
    st.write(f"**FN :** {fn}")
    st.write(f"**DOB :** {dob.isoformat()} — Âge actuel : {age_now} ans ; Âge à l'émission : {age_at_issue} ans")
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
