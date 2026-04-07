# driver_license_uiux_compact.py
# Aperçu UI/UX compact — 3 sections (gauche / centre / droite)
# Sexe = référence d'alignement
# Dépendances : streamlit, pandas
# pip install streamlit pandas

import streamlit as st
import datetime
import hashlib
import random

st.set_page_config(page_title="Aperçu Permis - Compact 3 Sections", layout="wide")

# -------------------------
# CSS compact
# -------------------------
st.markdown("""
<style>
:root{
  --bg:#f6f8fb; --card:#ffffff; --accent:#2563eb; --muted:#6b7280; --shadow:0 6px 18px rgba(2,6,23,0.08);
}
body { background:var(--bg); font-family:"Segoe UI", Roboto, Arial, sans-serif; color:#0f172a; }
.card { background:var(--card); border-radius:10px; padding:14px; box-shadow:var(--shadow); margin-bottom:14px; }

/* Layout 3 colonnes */
.three-cols { display:flex; gap:12px; align-items:flex-start; }
.col-left { width:30%; min-width:200px; border-radius:8px; padding:10px; background: linear-gradient(135deg, rgba(37,99,235,0.04), rgba(124,58,237,0.02)); }
.col-center { width:40%; min-width:280px; border-radius:8px; padding:10px; }
.col-right { flex:1; border-radius:8px; padding:10px; }

/* Grille interne : 1ère colonne = référence (Sexe) */
.info-grid {
  display:grid;
  grid-template-columns: 140px 1fr;
  gap:6px 12px;
  align-items:start;
}
.ref-col { display:flex; flex-direction:column; align-items:flex-start; }
.right-col { display:flex; flex-direction:column; gap:6px; }

/* Typographie compacte */
.label { font-size:11px; color:var(--muted); }
.value { font-size:14px; color:#0f172a; font-weight:700; }
.sub { font-size:12px; color:var(--muted); }
.badge { background: linear-gradient(90deg,var(--accent),#7c3aed); color:white; padding:4px 8px; border-radius:999px; font-weight:700; font-size:12px; }

/* Responsive */
@media (max-width:900px) {
  .three-cols { flex-direction:column; }
  .info-grid { grid-template-columns: 1fr; }
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

def format_date_us(d: datetime.date) -> str:
    return d.strftime("%m/%d/%Y")

def format_height(feet: int, inches: int) -> str:
    return f"{feet}'-{inches:02d}\""

# -------------------------
# Formulaire
# -------------------------
st.title("Générateur Permis — Compact 3 Sections")
st.caption("Disposition compacte : gauche = identification, centre = identité (Sexe référence), droite = compléments.")

with st.form(key="form_main"):
    ln = st.text_input("Nom de famille (LN)", value="HARMS")
    fn = st.text_input("Prénom (FN)", value="ROSA")
    dob = st.date_input("Date de naissance (DOB)", value=datetime.date(1995, 3, 15))
    sex = st.selectbox("Sexe (SEX)", ["M", "F", "X"], index=1)
    hgt_feet = st.number_input("Taille - pieds", min_value=0, max_value=8, value=5)
    hgt_inches = st.number_input("Taille - pouces", min_value=0, max_value=11, value=10)
    wgt = st.number_input("Poids (lbs)", min_value=50, max_value=400, value=160)
    hair = st.text_input("Cheveux (HAIR, 3 lettres)", value="BRN")
    eyes = st.text_input("Yeux (EYES, 3 lettres)", value="BLU")
    iss = st.date_input("Date d’émission (ISS)", value=datetime.date(2024, 6, 10))
    fo = st.selectbox("Bureau (Field Office)", [
        "San Jose (654) - Silicon Valley",
        "Fresno (210) - Central Valley",
        "Oakland (987) - East Bay",
        "Riverside (543) - Inland Empire",
        "Santa Ana (876) - Orange County"
    ])
    class_ = st.text_input("Classe (CLASS)", value="C")
    rstr = st.text_input("Restrictions (RSTR)", value="NONE")
    end = st.text_input("Endorsements (END)", value="")
    submit = st.form_submit_button("⚙️ Générer l'aperçu")

# -------------------------
# Rendu compact
# -------------------------
if submit:
    rnd = random.Random(deterministic_seed(ln, fn, dob.isoformat()))
    dl_number = random_letter(rnd) + random_digits(rnd, 7)
    exp_date = iss.replace(year=iss.year + 6)
    dob_str = format_date_us(dob)
    iss_str = format_date_us(iss)
    exp_str = format_date_us(exp_date)
    ln_u, fn_u = ln.upper(), fn.upper()
    hair_u = hair.upper()[:3].ljust(3, "X")
    eyes_u = eyes.upper()[:3].ljust(3, "X")
    hgt = format_height(int(hgt_feet), int(hgt_inches))
    dd = f"{iss_str.replace('/','')}{random_digits(rnd,6)}"
    generated_at = datetime.datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S")

    result = {
        "DL_NUMBER": dl_number, "LN": ln_u, "FN": fn_u, "SEX": sex, "DOB": dob_str,
        "HGT": hgt, "WGT": f"{wgt} lb", "HAIR": hair_u, "EYES": eyes_u,
        "ISS": iss_str, "EXP": exp_str, "CLASS": class_, "FO": fo, "DD": dd,
        "RSTR": rstr, "END": end, "GENERATED_AT": generated_at
    }

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;'>"
                f"<div><h3 style='margin:0'>Aperçu officiel</h3><div class='sub'>Disposition compacte en trois sections</div></div>"
                f"<div class='badge'>DL #{dl_number}</div></div>", unsafe_allow_html=True)

    # Trois sections côte à côte
    st.markdown("<div class='three-cols'>", unsafe_allow_html=True)

    # Section gauche
    st.markdown("<div class='col-left'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Bureau</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='value'>{result['FO']}</div>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Document ID</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>{result['DD']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Section centre
    st.markdown("<div class='col-center'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Nom</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='value'>{result['LN']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>Prénom: {result['FN']}</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    st.markdown("<div class='info-grid'>", unsafe_allow_html=True)
    st.markdown("<div class='ref-col'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Sexe</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='value'>{result['SEX']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>NéD’accord Fanomezantsoa, je t’ai préparé une version **compacte et bien organisée en trois sections** pour ton UI/UX. L’espace est minimisé, mais chaque bloc reste clair et aligné sur la référence *Sexe*.  

### Organisation des trois sections (30% / 40% / 30%)
- **Section gauche (Identification)**  
  Bureau, Document ID, encart visuel discret.  
- **Section centre (Identité & Sexe référence)**  
  Nom / Prénom, bloc *Sexe*, Taille / Poids, Yeux / Cheveux / Classe, Dates.  
- **Section droite (Compléments)**  
  Numéro de permis, Restrictions, Endorsements, Généré le.  

### Script Streamlit compact

```python
# driver_license_uiux_compact3.py
# Aperçu UI/UX compact — 3 sections alignées (Sexe = référence)
# pip install streamlit pandas

import streamlit as st
import datetime, hashlib, random

st.set_page_config(page_title="Aperçu Permis - Compact 3 Sections", layout="wide")

# --- CSS compact ---
st.markdown("""
<style>
.card {background:#fff; border-radius:10px; padding:12px; box-shadow:0 6px 18px rgba(2,6,23,0.08);}
.three-cols {display:flex; gap:12px;}
.col-left {width:30%; min-width:200px; padding:10px; background:linear-gradient(135deg,#e6eefc,#f3eefe);}
.col-center {width:40%; min-width:280px; padding:10px;}
.col-right {flex:1; padding:10px;}
.info-grid {display:grid; grid-template-columns:140px 1fr; gap:6px 12px;}
.label {font-size:11px; color:#6b7280;}
.value {font-size:14px; font-weight:700; color:#0f172a;}
.sub {font-size:12px; color:#6b7280;}
.badge {background:linear-gradient(90deg,#2563eb,#7c3aed); color:#fff; padding:4px 8px; border-radius:999px; font-size:12px; font-weight:700;}
@media(max-width:900px){.three-cols{flex-direction:column}.info-grid{grid-template-columns:1fr}}
</style>
""", unsafe_allow_html=True)

# --- Utilitaires ---
def deterministic_seed(*parts): return int(hashlib.md5("|".join(parts).encode()).hexdigest()[:8],16)
def random_digits(rnd,l): return "".join(rnd.choice("0123456789") for _ in range(l))
def random_letter(rnd): return rnd.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
def format_date_us(d): return d.strftime("%m/%d/%Y")
def format_height(f,i): return f"{f}'-{i:02d}\""

# --- Formulaire ---
st.title("Générateur Permis — Compact 3 Sections")
ln = st.text_input("Nom de famille", "HARMS")
fn = st.text_input("Prénom", "ROSA")
dob = st.date_input("Date de naissance", datetime.date(1995,3,15))
sex = st.selectbox("Sexe", ["M","F","X"],1)
hgt_feet = st.number_input("Taille - pieds",0,8,5)
hgt_inches = st.number_input("Taille - pouces",0,11,10)
wgt = st.number_input("Poids (lbs)",50,400,160)
hair = st.text_input("Cheveux", "BRN")
eyes = st.text_input("Yeux", "BLU")
iss = st.date_input("Date d’émission", datetime.date(2024,6,10))
fo = st.selectbox("Bureau", ["San Jose (654) - Silicon Valley","Fresno","Oakland","Riverside","Santa Ana"])
class_ = st.text_input("Classe", "C")
rstr = st.text_input("Restrictions", "NONE")
end = st.text_input("Endorsements", "")
submit = st.button("⚙️ Générer l'aperçu")

# --- Aperçu ---
if submit:
    rnd = random.Random(deterministic_seed(ln,fn,dob.isoformat()))
    dl_number = random_letter(rnd)+random_digits(rnd,7)
    exp_date = iss.replace(year=iss.year+6)
    result = {
        "DL_NUMBER":dl_number,"LN":ln.upper(),"FN":fn.upper(),"SEX":sex,
        "DOB":format_date_us(dob),"HGT":format_height(hgt_feet,hgt_inches),
        "WGT":f"{wgt} lb","HAIR":hair.upper(),"EYES":eyes.upper(),
        "ISS":format_date_us(iss),"EXP":format_date_us(exp_date),
        "CLASS":class_,"FO":fo,"DD":format_date_us(iss).replace("/","")+random_digits(rnd,6),
        "RSTR":rstr,"END":end,"GENERATED_AT":datetime.datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S")
    }

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>"
                f"<div><h3>Aperçu officiel</h3><div class='sub'>Disposition compacte en trois sections</div></div>"
                f"<div class='badge'>DL #{result['DL_NUMBER']}</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='three-cols'>", unsafe_allow_html=True)

    # Gauche
    st.markdown(f"<div class='col-left'><div class='label'>Bureau</div><div class='value'>{result['FO']}</div>"
                f"<div class='label'>Document ID</div><div class='sub'>{result['DD']}</div></div>", unsafe_allow_html=True)

    # Centre
    st.markdown("<div class='col-center'>", unsafe_allow_html=True)
    st.markdown(f"<div class='label'>Nom</div><div class='value'>{result['LN']}</div><div class='sub'>Prénom: {result['FN']}</div>", unsafe_allow_html=True)
    st.markdown("<div class='info-grid'>", unsafe_allow_html=True)
    st.markdown(f"<div class='ref-col'><div class='label'>Sexe</div><div class='value'>{result['SEX']}</div><div class='sub'>Né(e): {result['DOB']}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='right-col'><div class='label'>Taille</div><div class='value'>{result['HGT']}</div><div class='sub'>Poids: {result['WGT']}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ref-col'><div class='label'>&nbsp;</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='right-col'><div class='label'>Yeux / Cheveux</div><div class='value'>{result['EYES']} / {result['HAIR']}</div><div class='sub'>Classe: {result['CLASS']}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='grid-column:1/-1;display:flex;gap:12px;margin-top:6px;'>"
                f"<div style='flex:1'><div class='label'>Émission</div><div class='value'>{result['ISS']}</div></div>"
                f"<div style='flex:1'><div class='label'>Expiration</div><div class='value'>{result['EXP']}</div></div></div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

    # Droite
    st.markdown(f"<div class='col-right'><div class='label'>Numéro de permis</div><div class='value'>{result['DL_NUMBER']}</div>"
                f"<div class='label'>Restrictions</div><div class='sub'>{result['RSTR']}</div>"
                f"<div class='label'>Endorsements</div><div class='sub'>{result['END']}</div>"
                f"<div class='sub'>Généré le: {result['GENERATED_AT']}</div></div>", unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)
    st.success("✅ Aperçu compact en trois sections généré.")
