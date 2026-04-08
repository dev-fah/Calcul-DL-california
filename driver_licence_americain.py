# driver_license_premium_compact_pdf417.py
# Générateur Permis Californie — Version Premium Compact avec PDF417
# Dépendances : streamlit, pypdf417, pillow
# Installer : pip install streamlit pypdf417 pillow

import streamlit as st
from datetime import date, datetime
import hashlib, random, io
import pypdf417
from PIL import Image

st.set_page_config(page_title="Permis Californie Premium Compact", layout="wide")

# -------------------------
# CSS premium compact
# -------------------------
st.markdown("""
<style>
:root{
  --bg:#f5f7fb; --card:#ffffff; --muted:#6b7280; --text:#0f172a;
  --accent:#1f6feb; --accent-2:#7c3aed;
  --shadow:0 6px 18px rgba(15,23,42,0.06); --radius:10px;
}
body { background:var(--bg); font-family:Inter,"Segoe UI",Roboto,Arial,sans-serif; color:var(--text); }
.container { max-width:1200px; margin:12px auto; padding:6px; }
.form-row { display:flex; gap:10px; margin-bottom:8px; }
.form-col { background:var(--card); border-radius:var(--radius); padding:10px; box-shadow:var(--shadow); }
.form-col.small { width:28%; min-width:220px; }
.form-col.medium { width:44%; min-width:320px; }
.form-col.large { flex:1; }
.preview { background:var(--card); border-radius:var(--radius); padding:10px; box-shadow:var(--shadow); margin-top:10px; }
.preview-row { display:flex; gap:10px; }
.col-left { width:30%; min-width:200px; padding:8px; border-radius:8px; background:linear-gradient(135deg,rgba(31,111,235,0.04),rgba(124,58,237,0.02)); }
.col-center { width:40%; min-width:300px; padding:8px; }
.col-right { flex:1; padding:8px; }
.info-grid { display:grid; grid-template-columns:120px 1fr; gap:6px 10px; }
.label { font-size:11px; color:var(--muted); margin-bottom:2px; }
.value { font-size:14px; font-weight:700; color:var(--text); }
.sub { font-size:12px; color:var(--muted); }
.badge { background:linear-gradient(90deg,var(--accent),var(--accent-2)); color:#fff; padding:4px 8px; border-radius:999px; font-weight:700; font-size:12px; }
@media(max-width:1000px){.form-row,.preview-row{flex-direction:column}.form-col.small,.form-col.medium,.form-col.large,.col-left,.col-center,.col-right{width:100%;min-width:unset}.info-grid{grid-template-columns:1fr}}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Utilitaires
# -------------------------
def seed(*x): return int(hashlib.md5("|".join(map(str,x)).encode()).hexdigest()[:8],16)
def rdigits(r,n): return "".join(r.choice("0123456789") for _ in range(n))
def rletter(r, initial): return initial.upper() if initial.isalpha() else r.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

# -------------------------
# Formulaire
# -------------------------
st.markdown("<div class='container'>", unsafe_allow_html=True)
st.title("Générateur Permis — Premium Compact")

with st.form("dl_form"):
    st.markdown("<div class='form-row'>", unsafe_allow_html=True)

    # Colonne gauche
    st.markdown("<div class='form-col small'>", unsafe_allow_html=True)
    ln = st.text_input("Nom de famille", "HARMS")
    fn = st.text_input("Prénom", "ROSA")
    sex = st.selectbox("Sexe", ["M","F"], index=1)
    dob = st.date_input("Date de naissance", date(1990,1,1))
    st.markdown("</div>", unsafe_allow_html=True)

    # Colonne centre
    st.markdown("<div class='form-col medium'>", unsafe_allow_html=True)
    h1 = st.number_input("Pieds",0,8,5)
    h2 = st.number_input("Pouces",0,11,10)
    w = st.number_input("Poids (lb)",30,500,160)
    eyes = st.text_input("Yeux","BLU")
    hair = st.text_input("Cheveux","BRN")
    st.markdown("</div>", unsafe_allow_html=True)

    # Colonne droite
    st.markdown("<div class='form-col large'>", unsafe_allow_html=True)
    cls = st.text_input("Classe","C")
    rstr = st.text_input("Restrictions","NONE")
    endorse = st.text_input("Endorsements","NONE")
    iss = st.date_input("Date d'émission", date.today())
    submit = st.form_submit_button("⚙️ Générer l'aperçu")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Génération + Aperçu
# -------------------------
if submit:
    r = random.Random(seed(ln,fn,dob))
    dl = rletter(r, ln[0]) + rdigits(r,7)
    exp_year = iss.year + 5
    exp = date(exp_year, dob.month, dob.day)

    # Chaîne AAMVA pour PDF417
    aamva_data = {
        "DCS": ln.upper(),
        "DCT": fn.upper(),
        "DAQ": dl,
        "DBB": dob.strftime("%Y%m%d"),
        "DAJ": "CA"
    }
    raw_string = "".join(f"{k}{v}" for k,v in aamva_data.items())
    codes = pypdf417.encode(raw_string)
    image = pypdf417.render_image(codes, scale=3)
    buf = io.BytesIO(); image.save(buf, format="PNG"); byte_im = buf.getvalue()

    # Aperçu officiel
    st.markdown("<div class='preview'>", unsafe_allow_html=True)
    st.markdown(f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>"
                f"<div><h3 style='margin:0'>Aperçu officiel</h3><div class='sub'>Fiche premium compacte</div></div>"
                f"<div class='badge'>DL #{dl}</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='preview-row'>", unsafe_allow_html=True)

    # Colonne gauche
    st.markdown("<div class='col-left'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Document ID</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>{raw_string[:12]}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Colonne centre
    st.markdown("<div class='col-center'>", unsafe_allow_html=True)
    st.markdown(f"<div class='label'>Nom</div><div class='value'>{ln.upper()}</div><div class='sub'>Prénom: {fn.upper()}</div>", unsafe_allow_html=True)
    st.markdown("<div class='info-grid'>", unsafe_allow_html=True)
    st.markdown(f"<div><div class='label'>Sexe</div><div class='value'>{sex}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div><div class='label'>Né(e)</div><div class='sub'>{dob}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div><div class='label'>Taille</div><div class='value'>{h1} ft {h2} in</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div><div class='label'>Poids</div><div class='value'>{w} lb</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div><div class='label'>Yeux</div><div class='value'>{eyes.upper()}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div><div class='label'>Cheveux</div><div class='value'>{hair.upper()}</div></div>",
