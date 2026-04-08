# app.py

import streamlit as st
from pdf417gen import encode, render_image, render_svg
import io

st.set_page_config(page_title="PDF417 California DL", layout="centered")
st.title("Générateur PDF417 - Permis Californie")
st.write("Projet académique : Encodage AAMVA en code-barres PDF417")

# -------------------------
# Formulaire d'entrée
# -------------------------
with st.form("dl_form"):
    nom = st.text_input("Nom de famille (DCS)", "DUPONT")
    prenom = st.text_input("Prénom (DCT)", "JEAN")
    dl_num = st.text_input("Numéro de permis (DAQ)", "I1234567")
    dob = st.date_input("Date de naissance (DBB)")
    
    output_format = st.selectbox("Format du code-barres", ["PNG", "SVG"])
    
    submit = st.form_submit_button("Générer le code-barres")

# -------------------------
# Génération PDF417
# -------------------------
if submit:
    # 1. Formater la date (AAAAMMJJ)
    dob_formatted = dob.strftime("%Y%m%d")
    
    # 2. Construire la chaîne AAMVA simplifiée
    raw_data = f"DCS{nom.upper()}DCT{prenom.upper()}DAQ{dl_num.upper()}DBB{dob_formatted}"
    
    # 3. Encodage PDF417
    codes = encode(raw_data, columns=10, security_level=2)
    
    if output_format.upper() == "PNG":
        image = render_image(codes, scale=3)
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.image(byte_im, caption=f"Données encodées : {raw_data}")
        st.download_button(
            label="Télécharger le code-barres (PNG)",
            data=byte_im,
            file_name="ca_dl_barcode.png",
            mime="image/png"
        )
    elif output_format.upper() == "SVG":
        svg_content = render_svg(codes, scale=3)
        st.code(svg_content, language="html")
        st.download_button(
            label="Télécharger le code-barres (SVG)",
            data=svg_content,
            file_name="ca_dl_barcode.svg",
            mime="image/svg+xml"
        )
