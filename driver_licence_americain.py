# driver_license_premium_compact_pdf417_resilient.py
# Générateur Permis Californie — Premium Compact avec gestion d'absence de pypdf417
# Dépendances recommandées : streamlit, pypdf417 (ou pdf417gen), pillow
# Installer si nécessaire : pip install streamlit pypdf417 pillow
# Alternative : pip install streamlit pdf417gen pillow

import streamlit as st
from datetime import date, datetime
import hashlib, random, io
from typing import Optional

# Essayer d'importer pypdf417, sinon pdf417gen, sinon None
pypdf417 = None
pdf417gen = None
pil_available = True
try:
    import pypdf417 as _p
    pypdf417 = _p
except Exception:
    try:
        import pdf417gen as _g
        pdf417gen = _g
    except Exception:
        pypdf417 = None
        pdf417gen = None

try:
    from PIL import Image
except Exception:
    pil_available = False

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
def seed(*x) -> int:
    return int(hashlib.md5("|".join(map(str,x)).encode()).hexdigest()[:8],16)

def rdigits(r: random.Random, n: int) -> str:
    return "".join(r.choice("0123456789") for _ in range(n))

def rletter(r: random.Random, initial: str) -> str:
    return initial.upper() if initial and initial[0].isalpha() else r.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def format_date(d: date) -> str:
    return d.strftime("%Y-%m-%d")

def format_height(feet: int, inches: int) -> str:
    return f"{feet} ft {inches} in"

# -------------------------
# Formulaire
# -------------------------
st.markdown("<div class='container'>", unsafe_allow_html=True)
st.title("Générateur Permis — Premium Compact (PDF417)")

with st.form("dl_form"):
    st.markdown("<div class='form-row'>", unsafe_allow_html=True)

    # Colonne gauche
    st.markdown("<div class='form-col small'>", unsafe_allow_html=True)
    ln = st.text_input("Nom de famille", "HARMS")
    fn = st.text_input("Prénom", "ROSA")
    sex = st.selectbox("Sexe", ["M","F","X"], index=1)
    dob = st.date_input("Date de naissance", date(1995,3,15))
    st.markdown("</div>", unsafe_allow_html=True)

    # Colonne centre
    st.markdown("<div class='form-col medium'>", unsafe_allow_html=True)
    h1 = st.number_input("Pieds",0,8,5)
    h2 = st.number_input("Pouces",0,11,10)
    w = st.number_input("Poids (lb)",30,500,160)
    eyes = st.text_input("Yeux (ex: BLU)", "BLU")
    hair = st.text_input("Cheveux (ex: BRN)", "BRN")
    st.markdown("</div>", unsafe_allow_html=True)

    # Colonne droite
    st.markdown("<div class='form-col large'>", unsafe_allow_html=True)
    cls = st.text_input("Classe", "C")
    rstr = st.text_input("Restrictions", "NONE")
    endorse = st.text_input("Endorsements", "NONE")
    iss = st.date_input("Date d'émission", date.today())
    submit = st.form_submit_button("⚙️ Générer l'aperçu")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Génération + Aperçu
# -------------------------
if submit:
    # seed + dl number
    r = random.Random(seed(ln, fn, dob))
    dl = rletter(r, ln[:1] if ln else "A") + rdigits(r, 7)
    exp_year = iss.year + 5
    try:
        exp = date(exp_year, dob.month, dob.day)
    except Exception:
        # fallback si date invalide (ex: 29 février)
        exp = date(exp_year, min(dob.month,12), min(dob.day,28))

    # Construire chaîne AAMVA (simple, minimale)
    aamva_data = {
        "DCS": ln.upper(),
        "DCT": fn.upper(),
        "DAQ": dl,
        "DBB": dob.strftime("%Y%m%d"),
        "DAJ": "CA"
    }
    raw_string = "".join(f"{k}{v}" for k, v in aamva_data.items())

    # Tenter de générer PDF417 (pypdf417 ou pdf417gen)
    barcode_png_bytes: Optional[bytes] = None
    barcode_error: Optional[str] = None

    if pypdf417 is not None and pil_available:
        try:
            codes = pypdf417.encode(raw_string)
            image = pypdf417.render_image(codes, scale=3)
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            barcode_png_bytes = buf.getvalue()
        except Exception as e:
            barcode_error = f"Erreur génération pypdf417: {e}"
    elif pdf417gen is not None and pil_available:
        try:
            # pdf417gen.render_image retourne PIL Image via pdf417gen
            codes = pdf417gen.encode(raw_string, columns=6)
            image = pdf417gen.render_image(codes, scale=3)  # peut varier selon version
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            barcode_png_bytes = buf.getvalue()
        except Exception as e:
            barcode_error = f"Erreur génération pdf417gen: {e}"
    else:
        # aucune lib disponible
        barcode_error = None

    # Aperçu officiel (premium compact)
    st.markdown("<div class='preview'>", unsafe_allow_html=True)
    st.markdown(f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>"
                f"<div><h3 style='margin:0'>Aperçu officiel</h3><div class='sub'>Fiche premium compacte</div></div>"
                f"<div class='badge'>DL #{dl}</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='preview-row'>", unsafe_allow_html=True)

    # Colonne gauche (administratif)
    st.markdown("<div class='col-left'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Document ID (extrait)</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>{raw_string[:24]}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Colonne centre (identité, alignée sur Sexe)
    st.markdown("<div class='col-center'>", unsafe_allow_html=True)
    st.markdown(f"<div class='label'>Nom</div><div class='value'>{ln.upper()}</div><div class='sub'>Prénom: {fn.upper()}</div>", unsafe_allow_html=True)
    st.markdown("<div class='info-grid'>", unsafe_allow_html=True)
    st.markdown(f"<div><div class='label'>Sexe</div><div class='value'>{sex}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div><div class='label'>Né(e)</div><div class='sub'>{format_date(dob)}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div><div class='label'>Taille</div><div class='value'>{format_height(int(h1), int(h2))}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div><div class='label'>Poids</div><div class='value'>{int(w)} lb</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div><div class='label'>Yeux</div><div class='value'>{eyes.upper()}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div><div class='label'>Cheveux</div><div class='value'>{hair.upper()}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='grid-column:1/3;display:flex;gap:10px;margin-top:6px;'><div style='flex:1'><div class='label'>Émission</div><div class='sub'>{format_date(iss)}</div></div><div style='flex:1'><div class='label'>Expiration</div><div class='sub'>{format_date(exp)}</div></div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)  # close info-grid
    st.markdown("</div>", unsafe_allow_html=True)  # close col-center

    # Colonne droite (compléments)
    st.markdown("<div class='col-right'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Numéro de permis</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='value'>{dl}</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Classe</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>{cls.upper()}</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Restrictions</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>{rstr.upper()}</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Endorsements</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>{endorse.upper()}</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>Généré le: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)  # close col-right

    st.markdown("</div>", unsafe_allow_html=True)  # close preview-row
    st.markdown("</div>", unsafe_allow_html=True)  # close preview

    # Affichage / téléchargement du PDF417 si disponible
    if barcode_png_bytes:
        st.image(barcode_png_bytes, caption="Code-barres PDF417 du permis", use_column_width=False)
        st.download_button(label="Télécharger le code-barres (PNG)", data=barcode_png_bytes, file_name="ca_pdf417.png", mime="image/png")
    else:
        # Pas de lib disponible ou erreur
        if barcode_error:
            st.error(f"Impossible de générer le PDF417 automatiquement. Détail: {barcode_error}")
        else:
            st.warning("Aucune bibliothèque PDF417 détectée (pypdf417 ou pdf417gen).")

        st.info("Tu peux installer pypdf417 (recommandé) ou pdf417gen sur l'environnement d'exécution :\n\n"
                "`pip install pypdf417 pillow`  ou  `pip install pdf417gen pillow`")

        # Proposer le raw AAMVA string en téléchargement pour génération externe
        st.markdown("**Raw AAMVA string (à utiliser pour générer le PDF417 ailleurs)**")
        st.code(raw_string, language="text")
        st.download_button(label="Télécharger la chaîne AAMVA (TXT)", data=raw_string.encode("utf-8"), file_name="aamva_string.txt", mime="text/plain")

    st.success("✅ Aperçu premium compact généré.")
st.markdown("</div>", unsafe_allow_html=True)
