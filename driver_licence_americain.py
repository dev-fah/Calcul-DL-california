import streamlit as st
import html
import re
import json
from datetime import date, datetime, timedelta
import hashlib
import random
import string

# ---------------------------
# app.py - Version finale complète
# - Génération DD selon format configurable inspiré de l'exemple :
#   Exemple cible : "09/30/201560221/21FD/20"
# - Template par défaut utilisé : "{ISS_MM/DD/YYYY}{FO}{BATCH}/{EXP_YY}{SEC}/{EXP_YY}"
# - SEC générée à partir d'un SHA-256 (extraction configurable)
# - BATCH dérivé du hash (séquence numérique courte) pour simuler le numéro d'impression/lot
# - Affiche composants DD séparément et la chaîne DD finale
# - Validation DOB/ISS/EXP inchangée
# ---------------------------

# ---------- Fonctions utilitaires ----------
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

def _sha256_upper(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest().upper()

def derive_batch_from_hash(hash_val: str, length: int = 5) -> str:
    """Extrait une séquence numérique (batch) depuis le hash en prenant les chiffres disponibles."""
    digits = ''.join([c for c in hash_val if c.isdigit()])
    if len(digits) < length:
        # fallback: take hex chars and convert to digits
        extra = ''.join([str(ord(c) % 10) for c in hash_val[:length]])
        digits += extra
    return digits[:length]

def derive_alpha_from_hash(hash_val: str, length: int = 2) -> str:
    """Extrait une séquence alphabétique depuis le hash (A-Z)."""
    letters = ''.join([c for c in hash_val if c.isalpha()])
    if len(letters) < length:
        # fallback: map hex chars to letters
        mapped = []
        for ch in hash_val:
            if len(mapped) >= length:
                break
            mapped.append(chr((ord(ch) % 26) + 65))
        letters += ''.join(mapped)
    return letters[:length]

def calc_dd_components(issue_date: date, exp_date: date, office_code: str, sec_length: int = 2, batch_length: int = 5) -> dict:
    """
    Retourne les composants du DD selon le template utilisé.
    Template par défaut (exemple cible) : "{ISS_MM/DD/YYYY}{FO}{BATCH}/{EXP_YY}{SEC}/{EXP_YY}"
    - ISS_MM/DD/YYYY : date d'émission formatée avec slash
    - FO : code du bureau (ex: 509)
    - BATCH : séquence numérique dérivée du hash (ex: 60221)
    - EXP_YY : 2 derniers chiffres de l'année d'expiration (ex: 21)
    - SEC : séquence alphanumérique de sécurité (ex: FD) extraite du SHA-256 (taille configurable)
    """
    iss_slash = issue_date.strftime("%m/%d/%Y")            # "09/30/2015"
    exp_yy = exp_date.strftime("%y")                      # "21"
    # base string for hashing: combine iss (no slash), office, exp_yy and a random salt for variability
    base_for_hash = issue_date.strftime("%m%d%Y") + office_code + exp_yy
    # include a deterministic salt to avoid collisions for same inputs across runs (optional)
    hash_val = _sha256_upper(base_for_hash)
    batch = derive_batch_from_hash(hash_val, length=batch_length)   # numeric batch like "60221"
    sec_alpha = derive_alpha_from_hash(hash_val, length=sec_length) # alpha part like "FD"
    # also provide a numeric sec if desired (last N hex digits)
    sec_hex = hash_val[-sec_length:].upper()
    return {
        "iss_slash": iss_slash,
        "fo_code": office_code,
        "batch": batch,
        "exp_yy": exp_yy,
        "sec_alpha": sec_alpha,
        "sec_hex": sec_hex,
        "hash_source": base_for_hash,
        "hash_sha256": hash_val
    }

def build_dd_from_components(components: dict, template: str = "{ISS}{FO}{BATCH}/{EXP}{SEC}/{EXP}") -> str:
    """
    Construit la chaîne DD à partir des composants et d'un template.
    Template placeholders:
      {ISS}   -> ISS_MM/DD/YYYY (iss_slash)
      {FO}    -> FO code
      {BATCH} -> batch numeric
      {EXP}   -> EXP_YY
      {SEC}   -> SEC (on utilisera sec_alpha)
    Exemple template par défaut : "{ISS}{FO}{BATCH}/{EXP}{SEC}/{EXP}"
    """
    dd = template.replace("{ISS}", components["iss_slash"]) \
                 .replace("{FO}", components["fo_code"]) \
                 .replace("{BATCH}", components["batch"]) \
                 .replace("{EXP}", components["exp_yy"]) \
                 .replace("{SEC}", components["sec_alpha"])
    return dd

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
    "DOB": "Date de naissance — format YYYY-MM-DD. Doit être ≤ aujourd'hui - 16 ans.",
    "ISS": "Date d'émission — format YYYY-MM-DD. Doit être antérieure à aujourd'hui.",
    "FO": "Code du bureau DMV — ex. 509 (Pasadena).",
    "SEC": "Séquence de sécurité extraite d'un SHA-256 (alpha part).",
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
</style>
"""

# ---------- App UI ----------
st.set_page_config(page_title="Calcul DL + DD (format cible)", layout="centered")
st.markdown(TOOLTIP_CSS, unsafe_allow_html=True)

st.title("Générateur DL + DD (format cible)")
st.caption("DD construit selon un template configurable. Exemple cible : '09/30/201560221/21FD/20'")

today = date.today()
min_dob_allowed = safe_subtract_years(today, 120)
max_dob_allowed = safe_subtract_years(today, 16)
max_iss_allowed = today - timedelta(days=1)

# Field Office codes (display with code)
office_codes = {
    "Pasadena (509)": "509",
    "Los Angeles (Hope St) (502)": "502",
    "San Francisco (503)": "503",
    "San Diego (501)": "501",
    "Sacramento (500)": "500",
    "San Jose (516)": "516",
    "Oakland (Claremont Ave) (504)": "504",
    "Santa Monica (548)": "548",
    "Hollywood (661)": "661",
    "Glendale (628)": "628",
    "Culver City (611)": "611",
    "Long Beach (507)": "507"
}

# Sidebar options for DD formatting
st.sidebar.header("Options DD")
security_alpha_length = st.sidebar.selectbox("Longueur SEC (lettres)", options=[2, 4], index=0)
batch_length = st.sidebar.selectbox("Longueur BATCH (chiffres)", options=[4, 5, 6], index=1)
# Template input (advanced) - default matches the example-like format
default_template = "{ISS}{FO}{BATCH}/{EXP}{SEC}/{EXP}"
template = st.sidebar.text_input("Template DD (placeholders: {ISS},{FO},{BATCH},{EXP},{SEC})", value=default_template)

col1, col2 = st.columns(2)

with col1:
    ln = st.text_input("Nom de famille (LN)", value="Harms")
    fn = st.text_input("Prénom (FN)", value="Rosa")
    dob = st.date_input("Date de naissance (DOB)", value=date(1990, 12, 31), min_value=min_dob_allowed, max_value=max_dob_allowed)
    iss = st.date_input("Date d'émission (ISS)", value=date(2015, 9, 30), max_value=max_iss_allowed)
    office_display = st.selectbox("Code du bureau DMV", options=list(office_codes.keys()))

with col2:
    sex = st.selectbox("Sexe (SEX)", options=["F", "M", "X"], index=0)
    hgt = st.text_input("Taille (HGT)", value="5'-08''")
    wgt = st.text_input("Poids (WGT)", value="175 lb")
    hair = st.text_input("Cheveux (HAIR)", value="BRN")
    eyes = st.text_input("Yeux (EYES)", value="BRO")
    pclass = st.text_input("Classe (CLASS)", value="C")
    rstr = st.text_input("Restrictions (RSTR)", value="NONE")
    end = st.text_input("Endorsements (END)", value="")

# ---------- Calcul ----------
if st.button("Calculer"):
    errors = []

    # Basic validations
    if not ln.strip():
        errors.append("Le nom de famille (LN) est obligatoire.")
    if not fn.strip():
        errors.append("Le prénom (FN) est obligatoire.")
    if not isinstance(dob, date):
        errors.append("Date de naissance invalide.")
    if not isinstance(iss, date):
        errors.append("Date d'émission invalide.")

    if isinstance(dob, date) and dob > max_dob_allowed:
        errors.append(f"DOB invalide : doit être au plus le {max_dob_allowed.isoformat()} (âge ≥ 16 ans).")
    if isinstance(iss, date) and iss >= today:
        errors.append("ISS invalide : doit être antérieure à aujourd'hui.")
    if isinstance(dob, date) and isinstance(iss, date) and iss <= dob:
        errors.append("ISS invalide : doit être postérieure à DOB.")

    exp = None
    if isinstance(dob, date) and isinstance(iss, date):
        exp = calc_expiration(dob, iss)
        if exp <= today:
            errors.append(f"EXP invalide ({exp.isoformat()}) : doit être strictement après {today.isoformat()}.")

    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    # Generate DL and DD components
    dl = calc_dl(ln, dob)
    office_code = office_codes[office_display]
    dd_components = calc_dd_components(iss, exp, office_code, sec_length=security_alpha_length, batch_length=batch_length)
    # Build DD string using template (SEC uses sec_alpha)
    dd = build_dd_from_components(dd_components, template=template)

    # Placeholder for uniqueness check in DB (implementation depends on your DB)
    # if db.exists({"DD": dd}): ...
    age_at_issue = calculate_age(dob, iss)
    age_now = calculate_age(dob, today)

    result = {
        "DL": dl,
        "DD": dd,
        "DD_components": dd_components,
        "DD_template_used": template,
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
        "OFFICE_DISPLAY": office_display,
        "OFFICE_CODE": office_code,
        "SEC_ALPHA_LENGTH": security_alpha_length,
        "BATCH_LENGTH": batch_length
    }

    # ---------- Affichage ----------
    st.subheader("Résultats simulés")
    st.write(f"**DL :** {dl}")
    st.write(f"**DD (final) :** {dd}")
    st.write(f"**Template utilisé :** {template}")
    st.write("**Composants DD détaillés :**")
    st.write(f"- ISS (MM/DD/YYYY) : {dd_components['iss_slash']}")
    st.write(f"- FO code : {dd_components['fo_code']}")
    st.write(f"- BATCH (numeric) : {dd_components['batch']}")
    st.write(f"- EXP_YY : {dd_components['exp_yy']}")
    st.write(f"- SEC (alpha) : {dd_components['sec_alpha']}")
    st.write(f"- SEC (hex tail) : {dd_components['sec_hex']}")
    st.write(f"- SHA-256 (full) : {dd_components['hash_sha256']}")
    st.write("---")
    st.write(f"**EXP :** {exp.isoformat()}  (doit être strictement après {today.isoformat()})")
    st.write(f"**ISS :** {iss.isoformat()}")
    st.write(f"**Office :** {office_display} — code {office_code}")
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
