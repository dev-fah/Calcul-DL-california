# driver_license_uiux_compact3_fixed.py
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
