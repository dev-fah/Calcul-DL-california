# driver_license_premium_compact_final_v2.py
# Générateur Permis — Version Premium Compact V2 (UI optimisée)
# pip install streamlit
# streamlit run driver_license_premium_compact_final_v2.py

import streamlit as st
import datetime, hashlib, random

st.set_page_config(page_title="Permis Premium Compact", layout="wide")

# -------------------------
# CSS PREMIUM (plus net, plus compact, plus aligné)
# -------------------------
st.markdown("""
<style>
:root{
  --bg:#f6f8fc;
  --card:#ffffff;
  --muted:#6b7280;
  --text:#0f172a;
  --accent:#2563eb;
  --accent2:#7c3aed;
  --border:#e5e7eb;
  --shadow:0 4px 14px rgba(0,0,0,0.05);
  --radius:10px;
}

html, body {
  background:var(--bg);
  font-family: Inter, system-ui, sans-serif;
  color:var(--text);
}

/* Container */
.container {
  max-width:1150px;
  margin:10px auto;
  padding:4px;
}

/* FORM */
.form-row {
  display:flex;
  gap:8px;
  margin-bottom:6px;
}

.form-col {
  background:var(--card);
  border-radius:var(--radius);
  padding:8px;
  box-shadow:var(--shadow);
  border:1px solid var(--border);
}

.form-col.small { width:26%; min-width:210px; }
.form-col.medium { width:40%; min-width:300px; }
.form-col.large { flex:1; }

/* Inputs ultra compacts */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stSelectbox div[data-baseweb="select"] {
  height:32px !important;
  font-size:12px !important;
  padding:4px 6px !important;
}

/* PREVIEW */
.preview {
  margin-top:8px;
  padding:10px;
  background:var(--card);
  border-radius:var(--radius);
  box-shadow:var(--shadow);
  border:1px solid var(--border);
}

/* 3 colonnes strictes */
.preview-row {
  display:flex;
  gap:8px;
}

/* colonnes */
.col-left {
  width:28%;
  padding:8px;
  border-radius:8px;
  background:linear-gradient(135deg, rgba(37,99,235,0.05), rgba(124,58,237,0.03));
}

.col-center {
  width:42%;
  padding:8px;
}

.col-right {
  flex:1;
  padding:8px;
}

/* GRID identité */
.info-grid {
  display:grid;
  grid-template-columns:110px 1fr;
  gap:6px 8px;
}

/* TYPO */
.label {
  font-size:10px;
  color:var(--muted);
  margin-bottom:1px;
}

.value {
  font-size:14px;
  font-weight:700;
}

.sub {
  font-size:11px;
  color:var(--muted);
}

/* badge */
.badge {
  background:linear-gradient(90deg,var(--accent),var(--accent2));
  color:white;
  padding:3px 8px;
  border-radius:999px;
  font-size:11px;
  font-weight:700;
}

/* Responsive propre */
@media (max-width: 1000px) {
  .form-row, .preview-row {
    flex-direction:column;
  }
  .form-col, .col-left, .col-center, .col-right {
    width:100% !important;
  }
  .info-grid {
    grid-template-columns:1fr;
  }
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Utils
# -------------------------
def seed(*x):
    return int(hashlib.md5("|".join(map(str,x)).encode()).hexdigest()[:8],16)

def rand_digits(r,n):
    return "".join(r.choice("0123456789") for _ in range(n))

def rand_letter(r):
    return r.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

# -------------------------
# UI
# -------------------------
st.markdown("<div class='container'>", unsafe_allow_html=True)
st.title("Permis — Premium Compact")

st.markdown("<div class='form-row'>", unsafe_allow_html=True)

# LEFT
st.markdown("<div class='form-col small'>", unsafe_allow_html=True)
fo = st.selectbox("Bureau", ["San Jose","Fresno","Oakland"])
doc = st.text_input("Doc ID")
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
# PREVIEW
# -------------------------
if gen:
    r = random.Random(seed(ln,fn,dob))
    dl = rand_letter(r)+rand_digits(r,7)
    exp = iss.replace(year=iss.year+6)

    st.markdown("<div class='preview'>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px'>
        <div>
            <div class='value'>Aperçu officiel</div>
            <div class='sub'>Version compacte premium</div>
        </div>
        <div class='badge'>DL {dl}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='preview-row'>", unsafe_allow_html=True)

    # LEFT
    st.markdown(f"""
    <div class='col-left'>
        <div class='label'>Bureau</div>
        <div class='value'>{fo}</div>

        <div style='height:6px'></div>

        <div class='label'>Document</div>
        <div class='sub'>{doc or rand_digits(r,8)}</div>
    </div>
    """, unsafe_allow_html=True)

    # CENTER (alignement SEXE = pivot)
    st.markdown(f"""
    <div class='col-center'>

      <div style='display:flex;justify-content:space-between;align-items:flex-start'>
        <div>
          <div class='label'>Nom</div>
          <div class='value'>{ln}</div>
          <div class='sub'>{fn}</div>
        </div>

        <div style='width:80px;text-align:center'>
          <div class='label'>Sexe</div>
          <div class='value'>{sex}</div>
        </div>
      </div>

      <div style='height:6px'></div>

      <div class='info-grid'>
        <div>
          <div class='label'>Naissance</div>
          <div class='sub'>{dob}</div>
        </div>

        <div>
          <div class='label'>Taille / Poids</div>
          <div class='value'>{h1}ft{h2} / {w}lb</div>
        </div>

        <div>
          <div class='label'>Yeux</div>
          <div class='value'>{eyes}</div>
        </div>

        <div>
          <div class='label'>Cheveux</div>
          <div class='value'>{hair}</div>
        </div>

        <div style='grid-column:1/3;display:flex;gap:8px'>
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
    </div>
    """, unsafe_allow_html=True)

    # RIGHT
    st.markdown(f"""
    <div class='col-right'>
        <div class='label'>Permis</div>
        <div class='value'>{dl}</div>

        <div style='height:6px'></div>

        <div class='label'>Classe</div>
        <div class='sub'>{cls}</div>

        <div class='label'>Restrictions</div>
        <div class='sub'>{rstr}</div>

        <div class='label'>Endorsements</div>
        <div class='sub'>{end}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    st.success("✔ Aperçu généré")

st.markdown("</div>", unsafe_allow_html=True)
