import streamlit as st
import html
import re
import json
from datetime import date, timedelta
import hashlib
import io
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import zipfile

# Try to import reportlab for PDF export; if missing, disable PDF option gracefully
pdf_supported = True
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
except Exception:
    pdf_supported = False

# ---------------------------
# Utilitaires
# ---------------------------

def safe_subtract_years(d: date, years: int) -> date:
    try:
        return date(d.year - years, d.month, d.day)
    except Exception:
        return date(d.year - years, 2, 28)

def calc_expiration(dob: date, issue_date: date) -> date:
    exp_year = issue_date.year + 5
    try:
        return date(exp_year, dob.month, dob.day)
    except Exception:
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

def _sha256_upper(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest().upper()

def derive_batch_from_hash(hash_val: str, length: int = 5) -> str:
    digits = ''.join([c for c in hash_val if c.isdigit()])
    if len(digits) < length:
        extra = ''.join([str(ord(c) % 10) for c in hash_val[:length]])
        digits += extra
    return digits[:length]

def derive_alpha_from_hash(hash_val: str, length: int = 2) -> str:
    letters = ''.join([c for c in hash_val if c.isalpha()])
    if len(letters) < length:
        mapped = []
        for ch in hash_val:
            if len(mapped) >= length:
                break
            mapped.append(chr((ord(ch) % 26) + 65))
        letters += ''.join(mapped)
    return letters[:length]

def calc_dd_components(issue_date: date, exp_date: date, office_code: str,
                       sec_alpha_length: int = 2, batch_length: int = 5) -> dict:
    iss_slash = issue_date.strftime("%m/%d/%Y")
    exp_yy = exp_date.strftime("%y")
    exp_yy_plus1 = f"{(exp_date.year + 1) % 100:02d}"
    base_for_hash = issue_date.strftime("%m%d%Y") + office_code + exp_yy
    hash_val = _sha256_upper(base_for_hash)
    batch = derive_batch_from_hash(hash_val, length=batch_length)
    sec_alpha = derive_alpha_from_hash(hash_val, length=sec_alpha_length)
    sec_hex = hash_val[-sec_alpha_length:].upper()
    return {
        "iss_slash": iss_slash,
        "fo_code": office_code,
        "batch": batch,
        "exp_yy": exp_yy,
        "exp_yy_plus1": exp_yy_plus1,
        "sec_alpha": sec_alpha,
        "sec_hex": sec_hex,
        "hash_source": base_for_hash,
        "hash_sha256": hash_val
    }

def build_dd_from_components(components: dict, template: str) -> str:
    dd = template.replace("{ISS}", components["iss_slash"]) \
                 .replace("{FO}", components["fo_code"]) \
                 .replace("{BATCH}", components["batch"]) \
                 .replace("{EXP}", components["exp_yy_plus1"]) \
                 .replace("{EXP_ALT}", components["exp_yy"]) \
                 .replace("{SEC}", components["sec_alpha"])
    return dd

def to_json_result(result: dict) -> bytes:
    return json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8")

# ---------------------------
# UI helpers
# ---------------------------

TOOLTIPS = {
    "DOB": "Date de naissance — doit être ≤ aujourd'hui - 16 ans.",
    "ISS": "Date d'émission — doit être antérieure à aujourd'hui.",
    "FO": "Bureau (Field Office) — sélectionnez le bureau d'impression.",
    "EXPORT": "Choisissez le format d'export. Les détails techniques sont inclus dans le fichier exporté."
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
.label-tooltip:hover .tooltip-text { visibility: visible; opacity: 1; transform: translateY(0); }
</style>
"""

# ---------------------------
# App UI
# ---------------------------

st.set_page_config(page_title="DL + DD Generator", layout="centered")
st.markdown(TOOLTIP_CSS, unsafe_allow_html=True)

st.title("Générateur DL et DD")
st.caption("UI épurée : les détails techniques sont inclus dans l'export. Choisissez le format d'export.")

today = date.today()
min_dob_allowed = safe_subtract_years(today, 120)
max_dob_allowed = safe_subtract_years(today, 16)
max_iss_allowed = today - timedelta(days=1)

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

# Sidebar options
st.sidebar.header("Options")
security_alpha_length = st.sidebar.selectbox("Longueur SEC (lettres)", options=[2, 4], index=0)
batch_length = st.sidebar.selectbox("Longueur BATCH (chiffres)", options=[4, 5, 6], index=1)
default_template = "{ISS}{BATCH}/{EXP}{SEC}/{EXP_ALT}"
template = st.sidebar.text_input("Template DD (placeholders: {ISS},{FO},{BATCH},{EXP},{EXP_ALT},{SEC})",
                                 value=default_template)

# Export formats menu: remove PDF if reportlab missing
export_options = ["JSON", "TXT", "CSV", "XLSX", "PNG", "PSD (archive)", "WEBHP (archive)"]
if pdf_supported:
    export_options.insert(5, "PDF")  # insert PDF before PSD

export_format = st.sidebar.selectbox("Format d'export (menu déroulant)", options=export_options)

# Form
col1, col2 = st.columns(2)

with col1:
    ln = st.text_input("Nom de famille (LN)", value="Harms")
    fn = st.text_input("Prénom (FN)", value="Rosa")
    st.markdown(label_with_tooltip("DOB", "Date de naissance (DOB, YYYY-MM-DD)"), unsafe_allow_html=True)
    dob = st.date_input("", value=date(1990, 12, 31), min_value=min_dob_allowed, max_value=max_dob_allowed)
    st.markdown(label_with_tooltip("ISS", "Date d'émission (ISS, YYYY-MM-DD)"), unsafe_allow_html=True)
    iss = st.date_input("", value=date(2015, 9, 30), max_value=max_iss_allowed)
    st.markdown(label_with_tooltip("FO", "Bureau (Field Office)"), unsafe_allow_html=True)
    office_display = st.selectbox("", options=list(office_codes.keys()))

with col2:
    sex = st.selectbox("Sexe (SEX)", options=["F", "M", "X"], index=0)
    hgt = st.text_input("Taille (HGT)", value="5'-08''")
    wgt = st.text_input("Poids (WGT)", value="175 lb")
    hair = st.text_input("Cheveux (HAIR)", value="BRN")
    eyes = st.text_input("Yeux (EYES)", value="BRO")
    pclass = st.text_input("Classe (CLASS)", value="C")
    rstr = st.text_input("Restrictions (RSTR)", value="NONE")
    end = st.text_input("Endorsements (END)", value="")

# Actions
if st.button("Calculer"):
    errors = []
    if not ln.strip():
        errors.append("Le nom de famille (LN) est obligatoire.")
    if not fn.strip():
        errors.append("Le prénom (FN) est obligatoire.")
    if not isinstance(dob, date):
        errors.append("Date de naissance invalide.")
    if not isinstance(iss, date):
        errors.append("Date d'émission invalide.")
    if isinstance(dob, date) and dob > max_dob_allowed:
        errors.append(f"La date de naissance doit être au plus le {max_dob_allowed.isoformat()} (âge ≥ 16 ans).")
    if isinstance(iss, date) and iss >= today:
        errors.append("La date d'émission doit être antérieure à aujourd'hui.")
    if isinstance(dob, date) and isinstance(iss, date) and iss <= dob:
        errors.append("La date d'émission doit être postérieure à la date de naissance.")

    exp = None
    if isinstance(dob, date) and isinstance(iss, date):
        exp = calc_expiration(dob, iss)
        if exp <= today:
            errors.append(f"La date d'expiration calculée ({exp.isoformat()}) n'est pas valide. Elle doit être strictement après {today.isoformat()}.")

    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    # Generate fields
    dl = calc_dl(ln, dob)
    office_code = office_codes[office_display]
    dd_components = calc_dd_components(iss, exp, office_code,
                                      sec_alpha_length=security_alpha_length,
                                      batch_length=batch_length)
    dd = build_dd_from_components(dd_components, template=template)

    age_at_issue = (iss.year - dob.year) - ((iss.month, iss.day) < (dob.month, dob.day))
    age_now = (today.year - dob.year) - ((today.month, today.day) < (dob.month, dob.day))

    result = {
        "DL": dl,
        "DD": dd,
        "DD_structure": template,
        "DD_components": dd_components,
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
        "OFFICE_CODE": office_code
    }

    # Display minimal UI
    st.subheader("Résultats (aperçu)")
    st.write(f"**DL :** {dl}")
    st.write(f"**DD :** {dd}")
    st.write(f"**EXP :** {exp.isoformat()}  (doit être strictement après {today.isoformat()})")
    st.write(f"**ISS :** {iss.isoformat()}")
    st.write(f"**Office :** {office_display} — code {office_code}")
    st.write("---")
    st.write(f"**Nom :** {ln} {fn}")
    st.write(f"**DOB :** {dob.isoformat()}  — **Âge maintenant :** {age_now} ans")

    # Prepare export bytes
    def make_json_bytes(obj: dict) -> bytes:
        return to_json_result(obj)

    def make_txt_bytes(obj: dict) -> bytes:
        return to_json_result(obj)

    def make_csv_bytes(obj: dict) -> bytes:
        flat = obj.copy()
        comps = flat.pop("DD_components", {})
        for k, v in comps.items():
            flat[f"DD_{k}"] = v
        df = pd.DataFrame([flat])
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        return buf.getvalue().encode("utf-8")

    def make_xlsx_bytes(obj: dict) -> bytes:
        flat = obj.copy()
        comps = flat.pop("DD_components", {})
        for k, v in comps.items():
            flat[f"DD_{k}"] = v
        df = pd.DataFrame([flat])
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="DL_DD")
        return buf.getvalue()

    def make_png_bytes(obj: dict) -> bytes:
        text_lines = [
            f"DL: {obj['DL']}",
            f"DD: {obj['DD']}",
            f"ISS: {obj['ISS']}",
            f"EXP: {obj['EXP']}",
            f"Name: {obj['LN']} {obj['FN']}",
            f"DOB: {obj['DOB']}"
        ]
        width, height = 900, 220 + 20 * len(text_lines)
        img = Image.new("RGB", (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 16)
        except Exception:
            font = ImageFont.load_default()
        y = 20
        for line in text_lines:
            draw.text((20, y), line, fill=(10, 10, 10), font=font)
            y += 28
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    def make_pdf_bytes(obj: dict) -> bytes:
        if not pdf_supported:
            raise RuntimeError("PDF export non disponible : module reportlab introuvable.")
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        x_margin = 40
        y = 800
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_margin, y, "DL / DD Export")
        y -= 24
        c.setFont("Helvetica", 10)
        lines = [
            f"DL: {obj['DL']}",
            f"DD: {obj['DD']}",
            f"ISS: {obj['ISS']}",
            f"EXP: {obj['EXP']}",
            f"Name: {obj['LN']} {obj['FN']}",
            f"DOB: {obj['DOB']}",
            f"Sexe: {obj['SEX']}",
            f"Taille: {obj['HGT']}  Poids: {obj['WGT']}"
        ]
        for line in lines:
            c.drawString(x_margin, y, line)
            y -= 18
        c.showPage()
        c.save()
        return buf.getvalue()

    def make_archive_bytes(obj: dict, archive_name: str) -> bytes:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr(f"{archive_name}.json", json.dumps(obj, ensure_ascii=False, indent=2))
            z.writestr(f"{archive_name}.png", make_png_bytes(obj))
            readme = ("Fichier généré automatiquement. Pour PSD/WEBHP, "
                      "ce zip contient une image PNG et le JSON complet.")
            z.writestr("README.txt", readme)
        return buf.getvalue()

    # Map selection -> bytes
    filename_base = f"dl_{dl}"
    try:
        if export_format == "JSON":
            data_bytes = make_json_bytes(result); file_name = f"{filename_base}.json"; mime = "application/json"
        elif export_format == "TXT":
            data_bytes = make_txt_bytes(result); file_name = f"{filename_base}.txt"; mime = "text/plain"
        elif export_format == "CSV":
            data_bytes = make_csv_bytes(result); file_name = f"{filename_base}.csv"; mime = "text/csv"
        elif export_format == "XLSX":
            data_bytes = make_xlsx_bytes(result); file_name = f"{filename_base}.xlsx"; mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif export_format == "PNG":
            data_bytes = make_png_bytes(result); file_name = f"{filename_base}.png"; mime = "image/png"
        elif export_format == "PDF":
            if not pdf_supported:
                st.error("Export PDF non disponible : module reportlab introuvable sur cet environnement.")
                st.stop()
            data_bytes = make_pdf_bytes(result); file_name = f"{filename_base}.pdf"; mime = "application/pdf"
        elif export_format == "PSD (archive)":
            data_bytes = make_archive_bytes(result, filename_base); file_name = f"{filename_base}_psd_placeholder.zip"; mime = "application/zip"
        elif export_format == "WEBHP (archive)":
            data_bytes = make_archive_bytes(result, filename_base); file_name = f"{filename_base}_webhp_placeholder.zip"; mime = "application/zip"
        else:
            st.error("Format d'export non supporté.")
            st.stop()
    except Exception as e:
        st.error(f"Erreur lors de la préparation du fichier d'export : {e}")
        st.stop()

    st.download_button(
        label=f"Télécharger ({export_format})",
        data=data_bytes,
        file_name=file_name,
        mime=mime
    )

    if st.checkbox("Afficher JSON complet (inclut détails techniques)"):
        st.subheader("JSON complet (technique)")
        st.code(json.dumps(result, ensure_ascii=False, indent=2), language="json")

# If PDF is not supported, show a small notice in the UI
if not pdf_supported:
    st.info("Note : l'export PDF est désactivé car le module 'reportlab' n'est pas installé sur cet environnement. "
            "Installez 'reportlab' pour activer l'export PDF.")
