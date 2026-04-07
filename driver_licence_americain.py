# driver_license_premium_compact.py
# Générateur Permis — Version Premium Compact
# Dépendances : streamlit
# pip install streamlit

import streamlit as st
import datetime, hashlib, random

st.set_page_config(page_title="Aperçu Permis - Premium Compact", layout="wide")

# -------------------------
# CSS premium compact
# -------------------------
st.markdown("""
<style>
:root{
  --bg:#f5f7fb;
  --card:#ffffff;
  --muted:#6b7280;
  --text:#0f172a;
  --accent:#1f6feb;
  --accent-2:#7c3aed;
  --shadow: 0 6px 18px rgba(15,23,42,0.06);
  --radius:10px;
}
body { background:var(--bg); font-family: Inter, "Segoe UI", Roboto, Arial, sans-serif; color:var(--text); }

/* Card wrapper */
.container { max-width:1200px; margin:12px auto; }

/* Compact form layout */
.form-row { display:flex; gap:10px; align-items:flex-start; margin-bottom:8px; }
.form-col { background:var(--card); border-radius:var(--radius); padding:10px; box-shadow:var(--shadow); }
.form-col.small { width:28%; min-width:220px; padding:8px; }
.form-col.medium { width:44%; min-width:320px; padding:8px; }
.form-col.large { flex:1; padding:8px; }

/* Compact inputs: reduce vertical spacing */
.stTextInput>div>div>input, .stNumberInput>div>div>input, .stDateInput>div>div>input, .stSelectbox>div>div>div {
  padding:6px 8px !important;
  height:34px !important;
  font-size:13px !important;
}

/* Preview card */
.preview { background:var(--card); border-radius:var(--radius); padding:10px; box-shadow:var(--shadow); margin-top:10px; }

/* Three columns preview */
.preview-row { display:flex; gap:10px; align-items:flex-start; }
.col-left { width:30%; min-width:200px; padding:8px; border-radius:8px; background:linear-gradient(135deg, rgba(31,111,235,0.04), rgba(124,58,237,0.02)); }
.col-center { width:40%; min-width:300px; padding:8px; border-radius:8px; }
.col-right { flex:1; padding:8px; border-radius:8px; }

/* Grid inside center */
.info-grid { display:grid; grid-template-columns:120px 1fr; gap:6px 10px; align-items:start; }

/* Typography */
.label { font-size:11px; color:var(--muted); margin-bottom:2px; }
.value { font-size:14px; color:var(--text); font-weight:700; }
.sub { font-size:12px; color:var(--muted); }

/* Badge */
.badge { display:inline-block; background:linear-gradient(90deg,var(--accent),var(--accent-2)); color:#fff; padding:4px 8px; border-radius:999px; font-weight:700; font-size:12px; }

/* Tight spacing for preview rows */
.row-compact { display:flex; gap:8px; align-items:center; }

/* Responsive */
@media (max-width:1000px) {
  .form-row, .preview-row { flex-direction:column; }
  .form-col.small, .form-col.medium, .form-col.large, .col-left, .col-center, .col-right { width:100%; min-width:unset; }
  .info-grid { grid-template-columns:1fr; }
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Utilitaires
# -------------------------
def deterministic_seed(*parts: str) -> int:
    key = "|".join([p or "" for p in parts])
    return int(hashlib.md5(key.encode("utf-8")).hexdigest()[:8], 16)

def random_digits(rnd: random.Random, length: int) -> str:
    return "".join(rnd.choice("0123456789") for _ in range(length))

def random_letter(rnd: random.Random) -> str:
    return rnd.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def format_date(d: datetime.date) -> str:
    return d.strftime("%Y-%m-%d")

def format_height(feet: int, inches: int) -> str:
    return f"{feet} ft {inches} in"

# -------------------------
# Formulaire (compact, colonnes côte à côte)
# -------------------------
st.markdown("<div class='container'>", unsafe_allow_html=True)
st.title("Générateur Permis — Premium Compact")
st.markdown("<div class='form-row'>", unsafe_allow_html=True)

# Colonne gauche (administratif compact)
st.markdown("<div class='form-col small'>", unsafe_allow_html=True)
fo = st.selectbox("Bureau (Field Office)", [
    "San Jose (654) - Silicon Valley",
    "Fresno (210) - Central Valley",
    "Oakland (987) - East Bay",
    "Riverside (543) - Inland Empire",
    "Santa Ana (876) - Orange County"
], index=0)
doc_id = st.text_input("Document ID", value="")
st.markdown("</div>", unsafe_allow_html=True)

# Colonne centre (identité compacte)
st.markdown("<div class='form-col medium'>", unsafe_allow_html=True)
col1, col2 = st.columns([1,1])
with col1:
    ln = st.text_input("Nom de famille", value="HARMS")
    dob = st.date_input("Date de naissance", value=datetime.date(1995,3,15))
with col2:
    fn = st.text_input("Prénom", value="ROSA")
    sex = st.selectbox("Sexe", ["M","F","X"], index=1)
hgt_feet = st.number_input("Taille - pieds", min_value=0, max_value=8, value=5)
hgt_inches = st.number_input("Taille - pouces", min_value=0, max_value=11, value=10)
wgt = st.number_input("Poids (lbs)", min_value=30, max_value=500, value=160)
st.markdown("</div>", unsafe_allow_html=True)

# Colonne droite (compléments compact)
st.markdown("<div class='form-col large'>", unsafe_allow_html=True)
class_ = st.text_input("Classe", value="C")
rstr = st.text_input("Restrictions", value="NONE")
end = st.text_input("Endorsements", value="")
iss = st.date_input("Date d’émission", value=datetime.date.today())
generate = st.button("⚙️ Générer l'aperçu")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # close form-row

# -------------------------
# Aperçu officiel (trois colonnes côte à côte)
# -------------------------
if generate:
    rnd = random.Random(deterministic_seed(ln, fn, format_date(dob)))
    dl_number = random_letter(rnd) + random_digits(rnd, 7)
    exp_date = iss.replace(year=iss.year + 6)
    generated_at = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    result = {
        "FO": fo,
        "DOC_ID": doc_id or (format_date(iss).replace("-", "") + random_digits(rnd, 4)),
        "LN": ln.upper(),
        "FN": fn.upper(),
        "SEX": sex,
        "DOB": format_date(dob),
        "HGT": format_height(int(hgt_feet), int(hgt_inches)),
        "WGT": f"{int(wgt)} lb",
        "HAIR": (st.session_state.get("hair") if "hair" in st.session_state else "").upper() or "BRN",
        "EYES": (st.session_state.get("eyes") if "eyes" in st.session_state else "").upper() or "BLU",
        "ISS": format_date(iss),
        "EXP": format_date(exp_date),
        "CLASS": class_.upper(),
        "RSTR": rstr.upper(),
        "END": end.upper(),
        "DL": dl_number,
        "GENERATED_AT": generated_at
    }

    st.markdown("<div class='preview'>", unsafe_allow_html=True)
    st.markdown(f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>"
                f"<div><h3 style='margin:0'>Aperçu officiel</h3><div class='sub'>Fiche premium compacte</div></div>"
                f"<div class='badge'>DL #{result['DL']}</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='preview-row'>", unsafe_allow_html=True)

    # Colonne gauche (administratif)
    st.markdown("<div class='col-left'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Bureau</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='value'>{result['FO']}</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Document ID</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>{result['DOC_ID']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Colonne centre (identité, alignée sur Sexe)
    st.markdown("<div class='col-center'>", unsafe_allow_html=True)
    st.markdown("<div style='display:flex;justify-content:space-between;align-items:flex-start;gap:12px;'>", unsafe_allow_html=True)
    st.markdown(f"<div style='flex:1'><div class='label'>Nom</div><div class='value'>{result['LN']}</div>"
                f"<div class='sub'>Prénom: {result['FN']}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='width:90px;text-align:center;'><div class='label'>Sexe</div><div class='value'>{result['SEX']}</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='info-grid'>", unsafe_allow_html=True)
    st.markdown(f"<div><div class='label'>Né(e)</div><div class='sub'>{result['DOB']}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div><div class='label'>Taille / Poids</div><div class='value'>{result['HGT']} / {result['WGT']}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div><div class='label'>Yeux</div><div class='value'>{result['EYES']}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div><div class='label'>Cheveux</div><div class='value'>{result['HAIR']}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='grid-column:1/3;display:flex;gap:10px;margin-top:6px;'><div style='flex:1'><div class='label'>Émission</div><div class='sub'>{result['ISS']}</div></div><div style='flex:1'><div class='label'>Expiration</div><div class='sub'>{result['EXP']}</div></div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)  # close info-grid
    st.markdown("</div>", unsafe_allow_html=True)  # close col-center

    # Colonne droite (compléments)
    st.markdown("<div class='col-right'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Numéro de permis</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='value'>{result['DL']}</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Classe</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>{result['CLASS']}</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Restrictions</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>{result['RSTR']}</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Endorsements</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>{result['END']}</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>Généré le: {result['GENERATED_AT']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)  # close col-right

    st.markdown("</div>", unsafe_allow_html=True)  # close preview-row
    st.markdown("</div>", unsafe_allow_html=True)  # close preview

    st.success("✅ Aperçu premium compact généré.")
st.markdown("</div>", unsafe_allow_html=True)  # close container
