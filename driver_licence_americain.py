# driver_licence_uiux_preview.py
# Générateur DL avec aperçu UI/UX visuel
# Dépendances : streamlit, pandas, xlsxwriter
# Installation : pip install streamlit pandas xlsxwriter

import streamlit as st
import pandas as pd
import datetime
import hashlib
import random
import json
from io import BytesIO

st.set_page_config(page_title="Générateur DL Officiel", layout="wide")

# -------------------------
# CSS global et carte DL
# -------------------------
st.markdown("""
<style>
:root {
  --bg: #f6f8fb;
  --card: #ffffff;
  --accent1: #2563eb;
  --accent2: #7c3aed;
  --muted: #6b7280;
  --success: #10b981;
}
body { background: var(--bg); font-family: 'Segoe UI', Roboto, Arial, sans-serif; color:#0f172a; }
.card { background: var(--card); border-radius:12px; padding:18px; box-shadow: 0 8px 24px rgba(15,23,42,0.06); }
.dl-card {
  width:100%; max-width:760px; margin: 0 auto; border-radius:12px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  padding:18px; box-shadow: 0 10px 30px rgba(2,6,23,0.08); display:flex; gap:18px;
}
.dl-left { width:42%; background: linear-gradient(135deg, rgba(37,99,235,0.06), rgba(124,58,237,0.04)); padding:12px; border-radius:10px; display:flex; flex-direction:column; align-items:center; justify-content:flex-start; }
.dl-photo { width:100%; height:160px; background:linear-gradient(90deg,#e6eefc,#f3eefe); border-radius:8px; display:flex; align-items:center; justify-content:center; color:var(--muted); font-weight:600; }
.dl-right { width:58%; display:flex; flex-direction:column; gap:8px; }
.dl-row { display:flex; justify-content:space-between; gap:8px; }
.dl-title { font-size:14px; font-weight:700; color:var(--accent1); }
.dl-field { font-size:13px; color:#0f172a; font-weight:600; }
.dl-sub { font-size:12px; color:var(--muted); }
.small { font-size:12px; color:var(--muted); }
.meta { margin-top:8px; font-size:12px; color:var(--muted); }
.badge { display:inline-block; padding:6px 10px; border-radius:999px; background:linear-gradient(90deg,var(--accent1),var(--accent2)); color:white; font-weight:700; font-size:13px; }
.grid-2 { display:grid; grid-template-columns: 1fr 1fr; gap:8px; }
@media (max-width: 880px) {
  .dl-card { flex-direction:column; }
  .dl-left, .dl-right { width:100%; }
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

def to_json_bytes(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")

def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

def to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Résultats")
    return buf.getvalue()

# -------------------------
# Formulaire (colonnes)
# -------------------------
st.title("🆔 Générateur DL et DD")
st.caption("Formulaire compact — aperçu visuel type permis de conduire")

with st.form(key="form_main"):
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Informations personnelles")
    c1, c2, c3 = st.columns([1.2,1.2,0.8])
    with c1:
        ln = st.text_input("Nom de famille (LN)", value="HARMS")
        dob = st.date_input("Date de naissance (DOB)", value=datetime.date(1995,3,15))
    with c2:
        fn = st.text_input("Prénom (FN)", value="ROSA")
        sex = st.selectbox("Sexe (SEX)", ["M","F","X"], index=1)
    with c3:
        st.write("")  # espace
        st.write("")
        st.write("")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Caractéristiques physiques")
    c4, c5, c6 = st.columns(3)
    with c4:
        hgt_feet = st.number_input("Taille - pieds", min_value=0, max_value=8, value=5)
    with c5:
        hgt_inches = st.number_input("Taille - pouces", min_value=0, max_value=11, value=10)
    with c6:
        wgt = st.number_input("Poids (lbs)", min_value=50, max_value=400, value=160)
    c7, c8 = st.columns(2)
    with c7:
        hair = st.text_input("Cheveux (HAIR, 3 lettres)", value="BRN")
    with c8:
        eyes = st.text_input("Yeux (EYES, 3 lettres)", value="BLU")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Détails administratifs")
    c9, c10 = st.columns(2)
    with c9:
        iss = st.date_input("Date d’émission (ISS)", value=datetime.date(2024,6,10))
    with c10:
        fo = st.selectbox("Bureau (Field Office)", [
            "San Jose (654) - Silicon Valley",
            "Fresno (210) - Central Valley",
            "Oakland (987) - East Bay",
            "Riverside (543) - Inland Empire",
            "Santa Ana (876) - Orange County"
        ])
    c11, c12, c13 = st.columns(3)
    with c11: class_ = st.text_input("Classe (CLASS)", value="C")
    with c12: rstr = st.text_input("Restrictions (RSTR)", value="NONE")
    with c13: end = st.text_input("Endorsements (END)", value="")
    st.markdown("</div>", unsafe_allow_html=True)

    calculate = st.form_submit_button("⚙️ Générer l'aperçu")

# -------------------------
# Génération et aperçu UI
# -------------------------
if calculate:
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

    result = {
        "DL_NUMBER": dl_number,
        "LN": ln_u,
        "FN": fn_u,
        "SEX": sex,
        "DOB": dob_str,
        "HGT": hgt,
        "WGT": f"{wgt} lb",
        "HAIR": hair_u,
        "EYES": eyes_u,
        "ISS": iss_str,
        "EXP": exp_str,
        "CLASS": class_,
        "RSTR": rstr,
        "END": end,
        "FO": fo,
        "DD": dd,
        "GENERATED_AT": datetime.datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S")
    }

    # Aperçu visuel UI/UX (carte permis)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div style='display:flex; justify-content:space-between; align-items:center; gap:16px;'>"
                "<div style='flex:1'><h3 style='margin:0'>Aperçu officiel</h3><p class='small' style='margin:4px 0 0 0'>Aperçu visuel du permis généré</p></div>"
                "<div style='display:flex; gap:8px; align-items:center'>"
                f"<div class='badge'>DL #{dl_number}</div>"
                "</div></div>", unsafe_allow_html=True)

    # Render DL card HTML
    dl_html = f"""
    <div class="dl-card" role="region" aria-label="Aperçu permis">
      <div class="dl-left">
        <div class="dl-photo">Photo</div>
        <div style="height:12px"></div>
        <div class="small">Bureau</div>
        <div class="dl-field">{result['FO']}</div>
        <div style="height:8px"></div>
        <div class="small">Document ID</div>
        <div class="dl-sub">{result['DD']}</div>
      </div>
      <div class="dl-right">
        <div class="dl-row">
          <div>
            <div class="dl-title">Nom</div>
            <div class="dl-field">{result['LN']}</div>
            <div class="dl-sub">Prénom: {result['FN']}</div>
          </div>
          <div style="text-align:right">
            <div class="dl-title">Sexe</div>
            <div class="dl-field">{result['SEX']}</div>
            <div class="dl-sub">Né(e): {result['DOB']}</div>
          </div>
        </div>

        <div class="dl-row" style="margin-top:8px">
          <div>
            <div class="dl-title">Taille</div>
            <div class="dl-field">{result['HGT']}</div>
            <div class="dl-sub">Poids: {result['WGT']}</div>
          </div>
          <div style="text-align:right">
            <div class="dl-title">Yeux / Cheveux</div>
            <div class="dl-field">{result['EYES']} / {result['HAIR']}</div>
            <div class="dl-sub">Classe: {result['CLASS']}</div>
          </div>
        </div>

        <div style="margin-top:12px" class="grid-2">
          <div>
            <div class="dl-sub">Date d'émission</div>
            <div class="dl-field">{result['ISS']}</div>
          </div>
          <div>
            <div class="dl-sub">Date d'expiration</div>
            <div class="dl-field">{result['EXP']}</div>
          </div>
        </div>

        <div class="meta">Généré le: {result['GENERATED_AT']}</div>
      </div>
    </div>
    """
    st.markdown(dl_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Téléchargements (boutons directs)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    colj, colc, colx = st.columns([1,1,1])
    with colj:
        st.download_button("⬇️ Télécharger en JSON", data=to_json_bytes(result),
                           file_name="dl_officiel.json", mime="application/json")
    with colc:
        st.download_button("⬇️ Télécharger en CSV", data=to_csv_bytes(pd.DataFrame([result])),
                           file_name="dl_officiel.csv", mime="text/csv")
    with colx:
        st.download_button("⬇️ Télécharger en XLSX", data=to_excel_bytes(pd.DataFrame([result])),
                           file_name="dl_officiel.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.success("✅ Génération terminée — aperçu affiché et fichiers prêts au téléchargement.")
