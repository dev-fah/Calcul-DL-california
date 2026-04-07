# driver_license_premium_compact_clean.py
# Version FULL propre — rendu UI réel (aucun HTML brut affiché)

import streamlit as st
import datetime, hashlib, random

st.set_page_config(page_title="Permis Premium", layout="wide")

# -------------------------
# CSS GLOBAL PREMIUM
# -------------------------
st.markdown("""
<style>
:root{
  --bg:#f6f8fc;
  --card:#ffffff;
  --text:#0f172a;
  --muted:#6b7280;
  --border:#e5e7eb;
  --accent:#2563eb;
  --accent2:#7c3aed;
  --shadow:0 4px 16px rgba(0,0,0,0.05);
  --radius:10px;
}

body { background:var(--bg); font-family:Inter, sans-serif; }

.container { max-width:1100px; margin:auto; }

.form-row, .preview-row {
  display:flex;
  gap:10px;
}

.form-col, .col {
  background:var(--card);
  border-radius:var(--radius);
  padding:10px;
  box-shadow:var(--shadow);
  border:1px solid var(--border);
}

.small { width:28%; }
.medium { width:40%; }
.large { flex:1; }

.left { width:28%; }
.center { width:42%; }
.right { flex:1; }

.label { font-size:11px; color:var(--muted); }
.value { font-size:14px; font-weight:700; }
.sub { font-size:12px; color:var(--muted); }

.badge {
  background:linear-gradient(90deg,var(--accent),var(--accent2));
  color:white;
  padding:4px 10px;
  border-radius:999px;
  font-size:12px;
  font-weight:700;
}

.preview {
  margin-top:10px;
}

@media (max-width:1000px){
  .form-row, .preview-row { flex-direction:column; }
  .small, .medium, .large, .left, .center, .right { width:100%; }
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# UTILS
# -------------------------
def seed(*x):
    return int(hashlib.md5("|".join(map(str,x)).encode()).hexdigest()[:8],16)

def rdigits(r,n):
    return "".join(r.choice("0123456789") for _ in range(n))

def rletter(r):
    return r.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def ui(html):
    st.markdown(html, unsafe_allow_html=True)

# -------------------------
# FORMULAIRE
# -------------------------
st.markdown("<div class='container'>", unsafe_allow_html=True)

st.title("Permis — Premium Compact")

st.markdown("<div class='form-row'>", unsafe_allow_html=True)

# LEFT
st.markdown("<div class='form-col small'>", unsafe_allow_html=True)
fo = st.selectbox("Bureau", ["San Jose","Fresno","Oakland"])
doc = st.text_input("Document ID")
st.markdown("</div>", unsafe_allow_html=True)

# CENTER
st.markdown("<div class='form-col medium'>", unsafe_allow_html=True)
c1,c2 = st.columns(2)
with c1:
    ln = st.text_input("Nom", "HARMS")
    dob = st.date_input("Naissance", datetime.date(1995,3,15))
with c2:
    fn = st.text_input("Prénom", "ROSA")
    sex = st.selectbox("Sexe", ["M","F","X"])

h1 = st.number_input("Pieds",0,8,5)
h2 = st.number_input("Pouces",0,11,10)
w = st.number_input("Poids",30,500,160)
hair = st.text_input("Cheveux","BRN")
eyes = st.text_input("Yeux","BLU")
st.markdown("</div>", unsafe_allow_html=True)

# RIGHT
st.markdown("<div class='form-col large'>", unsafe_allow_html=True)
cls = st.text_input("Classe","C")
rstr = st.text_input("Restrictions","NONE")
end = st.text_input("Endorsements","")
iss = st.date_input("Émission", datetime.date.today())
gen = st.button("Générer")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# APERCU
# -------------------------
if gen:
    r = random.Random(seed(ln,fn,dob))
    dl = rletter(r)+rdigits(r,7)
    exp = iss.replace(year=iss.year+6)

    ui("<div class='preview'>")

    ui(f"""
    <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px'>
        <div>
            <div class='value'>Aperçu officiel</div>
            <div class='sub'>Version compacte premium</div>
        </div>
        <div class='badge'>DL {dl}</div>
    </div>
    """)

    ui("<div class='preview-row'>")

    # LEFT
    ui(f"""
    <div class='col left'>
        <div class='label'>Bureau</div>
        <div class='value'>{fo}</div>

        <br>

        <div class='label'>Document</div>
        <div class='sub'>{doc or rdigits(r,8)}</div>
    </div>
    """)

    # CENTER
    ui(f"""
    <div class='col center'>

        <div style='display:flex;justify-content:space-between'>
            <div>
                <div class='label'>Nom</div>
                <div class='value'>{ln}</div>
                <div class='sub'>{fn}</div>
            </div>

            <div style='text-align:center'>
                <div class='label'>Sexe</div>
                <div class='value'>{sex}</div>
            </div>
        </div>

        <br>

        <div class='label'>Naissance</div>
        <div class='sub'>{dob}</div>

        <div class='label'>Taille / Poids</div>
        <div class='value'>{h1}ft{h2} / {w}lb</div>

        <div class='label'>Yeux</div>
        <div class='value'>{eyes}</div>

        <div class='label'>Cheveux</div>
        <div class='value'>{hair}</div>

        <br>

        <div style='display:flex;gap:10px'>
            <div>
                <div class='label'>Émis</div>
                <div class='sub'>{iss}</div>
            </div>
            <div>
                <div class='label'>Expire</div>
                <div class='sub'>{exp}</div>
            </div>
        </div>

    </div>
    """)

    # RIGHT
    ui(f"""
    <div class='col right'>
        <div class='label'>Permis</div>
        <div class='value'>{dl}</div>

        <br>

        <div class='label'>Classe</div>
        <div class='sub'>{cls}</div>

        <div class='label'>Restrictions</div>
        <div class='sub'>{rstr}</div>

        <div class='label'>Endorsements</div>
        <div class='sub'>{end}</div>
    </div>
    """)

    ui("</div></div>")

    st.success("✔ Aperçu généré")

st.markdown("</div>", unsafe_allow_html=True)
