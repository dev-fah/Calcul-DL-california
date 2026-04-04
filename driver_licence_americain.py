# driver_licence_americain.py
import streamlit as st
import pandas as pd
import datetime
import hashlib, random, json
from io import BytesIO

st.set_page_config(page_title="Générateur DL et DD", layout="wide")

# --- CSS custom pour UI moderne ---
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #f0f4ff 0%, #ffffff 100%);
}
h1 {
    font-family: 'Segoe UI', sans-serif;
    font-weight: 700;
    color: #1e3a8a;
}
.preview-card {
    border-radius: 12px;
    padding: 16px;
    background: #ffffff;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    margin-bottom: 12px;
}
.kv-label {
    font-size: 13px;
    color: #6b7280;
}
.kv-value {
    font-size: 16px;
    font-weight: 600;
    color: #111827;
}
.stButton>button {
    background: linear-gradient(90deg,#2563eb,#4f46e5);
    color: white;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# --- Fonctions utilitaires ---
def deterministic_seed(*parts: str) -> int:
    key = "|".join([p or "" for p in parts])
    return int(hashlib.md5(key.encode()).hexdigest()[:8], 16)

def random_digits(rnd, length): return "".join(rnd.choice("0123456789") for _ in range(length))
def random_letters(rnd, length): return "".join(rnd.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(length))
def format_height(feet,inches): return f"{feet}'-{inches:02d}\""

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Paramètres avancés")
    sec_len = st.number_input("Longueur SEC",1,10,2)
    batch_len = st.number_input("Longueur BATCH",1,10,5)
    st.caption("UI épurée : détails techniques inclus dans l’export.")

# --- Formulaire principal ---
st.title("✦ Générateur DL et DD")
st.write("Remplissez les champs ci‑dessous et générez un aperçu élégant de vos données.")

with st.form("form_main"):
    ln = st.text_input("Nom de famille (LN)","Harms")
    fn = st.text_input("Prénom (FN)","Rosa")
    sex = st.selectbox("Sexe (SEX)",["M","F","Autre"])
    dob = st.date_input("Date de naissance",datetime.date(1995,12,14))
    hgt_feet = st.number_input("Taille - pieds",0,8,5)
    hgt_inches = st.number_input("Taille - pouces",0,11,8)
    wgt = st.text_input("Poids (WGT)","175 lb")
    iss = st.date_input("Date d’émission",datetime.date(2015,9,30))
    hair = st.text_input("Cheveux (HAIR)","BRN")
    eyes = st.text_input("Yeux (EYES)","BRO")
    fo = st.text_input("Bureau (Field Office)","Pasadena (509)")
    class_ = st.text_input("Classe (CLASS)","C")
    rstr = st.text_input("Restrictions (RSTR)","NONE")
    end = st.text_input("Endorsements (END)","")
    export_format = st.selectbox("Format d’export",["JSON","CSV","XLSX"])
    submit = st.form_submit_button("🚀 Calculer")

# --- Résultat ---
if submit:
    rnd = random.Random(deterministic_seed(ln,fn,dob.isoformat()))
    batch = random_digits(rnd,batch_len)
    sec = random_letters(rnd,sec_len)
    seq = random_digits(rnd,6)
    exp = iss.replace(year=iss.year+5)
    dl_number = f"{ln[:2].upper()}{fn[:2].upper()}{batch}{seq}"
    hgt = format_height(hgt_feet,hgt_inches)

    result = {
        "LN":ln,"FN":fn,"SEX":sex,"HGT":hgt,"DOB":dob.isoformat(),
        "WGT":wgt,"ISS":iss.isoformat(),"EXP":exp.isoformat(),
        "HAIR":hair,"EYES":eyes,"FO":fo,"CLASS":class_,"RSTR":rstr,
        "END":end,"DL_NUMBER":dl_number,"BATCH":batch,"SEC":sec,"SEQ":seq
    }

    st.subheader("✨ Aperçu élégant")
    cols = st.columns(3)
    with cols[0]:
        st.markdown(f"<div class='preview-card'><div class='kv-label'>Nom</div><div class='kv-value'>{ln}</div></div>",unsafe_allow_html=True)
        st.markdown(f"<div class='preview-card'><div class='kv-label'>Prénom</div><div class='kv-value'>{fn}</div></div>",unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<div class='preview-card'><div class='kv-label'>Sexe</div><div class='kv-value'>{sex}</div></div>",unsafe_allow_html=True)
        st.markdown(f"<div class='preview-card'><div class='kv-label'>Taille</div><div class='kv-value'>{hgt}</div></div>",unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f"<div class='preview-card'><div class='kv-label'>DL Number</div><div class='kv-value'>{dl_number}</div></div>",unsafe_allow_html=True)
        st.markdown(f"<div class='preview-card'><div class='kv-label'>Expiration</div><div class='kv-value'>{exp}</div></div>",unsafe_allow_html=True)

    with st.expander("🔧 Détails techniques"):
        st.json({"BATCH":batch,"SEC":sec,"SEQ":seq})

    # Export
    if export_format=="JSON":
        data = json.dumps(result,indent=2).encode()
        mime="application/json"; fname="dl_dd.json"
    elif export_format=="CSV":
        data = pd.DataFrame([result]).to_csv(index=False).encode()
        mime="text/csv"; fname="dl_dd.csv"
    else:
        buf=BytesIO()
        with pd.ExcelWriter(buf,engine="openpyxl") as w: pd.DataFrame([result]).to_excel(w,index=False)
        data=buf.getvalue(); mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"; fname="dl_dd.xlsx"

    st.download_button("⬇️ Télécharger",data=data,file_name=fname,mime=mime)
    st.success("Génération terminée — télécharge le fichier si besoin.")
