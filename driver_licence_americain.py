# streamlit_app_fixed_minimal.py
# Version corrigée minimale du script original.
# Même interface et logique que ton script initial, gestion propre de l'absence de pypdf417.
# Dépendances recommandées pour génération automatique : pypdf417, pillow
# Installer si possible : pip install pypdf417 pillow
# Si pypdf417 n'est pas disponible, le script fournit la chaîne AAMVA brute pour génération externe.

import streamlit as st
from datetime import date, datetime
import hashlib, random, io

# Tentative d'import de pypdf417 (ne modifie pas l'interface si absent)
pypdf417 = None
pil_available = True
try:
    import pypdf417 as _p
    pypdf417 = _p
except Exception:
    pypdf417 = None

try:
    from PIL import Image
except Exception:
    pil_available = False

st.set_page_config(page_title="Permis Californie PDF417", layout="centered")
st.title("Générateur Académique de Permis Californie")
st.write("Système interactif pour générer un permis CA avec code-barres PDF417 (AAMVA)")

# --- Fonction utilitaire ---
def seed(*x):
    return int(hashlib.md5("|".join(map(str,x)).encode()).hexdigest()[:8],16)

def rdigits(r,n):
    return "".join(r.choice("0123456789") for _ in range(n))

def rletter(r, initial):
    return initial.upper() if initial and initial.isalpha() else r.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def next_sequence(r):
    return str(r.randint(10,99))

# --- Formulaire (identique à l'original) ---
with st.form("dl_form"):
    ln = st.text_input("Nom de famille", "HARMS")
    fn = st.text_input("Prénom", "ROSA")
    sex = st.selectbox("Sexe", ["M","F"])
    dob = st.date_input("Date de naissance", date(1990,1,1))
    
    col1, col2 = st.columns(2)
    with col1:
        h1 = st.number_input("Pieds",0,8,5)
        w = st.number_input("Poids (lb)",30,500,160)
    with col2:
        h2 = st.number_input("Pouces",0,11,10)
        eyes = st.text_input("Yeux","BRN")
    hair = st.text_input("Cheveux","BRN")
    cls = st.text_input("Classe","C")
    rstr = st.text_input("Restrictions","NONE")
    endorse = st.text_input("Endorsements","NONE")
    iss = st.date_input("Date d'émission", date.today())
    
    submit = st.form_submit_button("Générer la carte")

# --- Génération (même logique, gestion d'erreur ajoutée) ---
if submit:
    # seed deterministe
    r = random.Random(seed(ln,fn,dob))
    dl = rletter(r, ln[:1] if ln else "A") + rdigits(r,7)
    
    # calcul expiration (5 ans)
    try:
        exp_year = iss.year + 5
        exp = date(exp_year, dob.month, dob.day)
    except Exception:
        # fallback si date invalide (ex: 29 février)
        exp = date(iss.year + 5, min(dob.month,12), min(dob.day,28))

    # Chaîne AAMVA minimale pour PDF417 (format simple, conforme à l'exemple)
    aamva_data = {
        "DCS": ln.upper(),
        "DCT": fn.upper(),
        "DAQ": dl,
        "DBB": dob.strftime("%Y%m%d"),
        "DAJ": "CA"
    }
    raw_string = "".join(f"{k}{v}" for k,v in aamva_data.items())

    # Tentative de génération PDF417 (si pypdf417 et pillow sont présents)
    barcode_png_bytes = None
    barcode_error = None

    if pypdf417 is not None and pil_available:
        try:
            codes = pypdf417.encode(raw_string)
            image = pypdf417.render_image(codes, scale=3)
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            barcode_png_bytes = buf.getvalue()
        except Exception as e:
            barcode_error = f"Erreur génération pypdf417: {e}"
    else:
        # pypdf417 absent ou PIL absent
        barcode_error = None

    # --- Affichage du résultat (interface inchangée) ---
    st.markdown("---")
    st.subheader("Aperçu officiel")
    st.write(f"**Nom:** {ln.upper()}  •  **Prénom:** {fn.upper()}")
    st.write(f"**Date de naissance:** {dob}  •  **Sexe:** {sex}")
    st.write(f"**Taille:** {h1} ft {h2} in  •  **Poids:** {w} lb")
    st.write(f"**Yeux:** {eyes.upper()}  •  **Cheveux:** {hair.upper()}")
    st.write(f"**Classe:** {cls.upper()}  •  **Restrictions:** {rstr.upper()}  •  **Endorsements:** {endorse.upper()}")
    st.write(f"**Numéro de permis:** {dl}")
    st.write(f"**Émission:** {iss}  •  **Expiration:** {exp}")
    st.write(f"**Document AAMVA (extrait):** {raw_string[:48]}")

    # --- Affichage / téléchargement du PDF417 si disponible, sinon message clair et raw string ---
    if barcode_png_bytes:
        st.image(barcode_png_bytes, caption="Code-barres PDF417 du permis", use_column_width=False)
        st.download_button(
            label="Télécharger le code-barres (PNG)",
            data=barcode_png_bytes,
            file_name="ca_pdf417.png",
            mime="image/png"
        )
    else:
        if barcode_error:
            st.error(f"Impossible de générer le PDF417 automatiquement. Détail: {barcode_error}")
        else:
            st.warning("La bibliothèque 'pypdf417' (ou 'pdf417gen') n'est pas installée dans cet environnement, ou 'Pillow' est manquant.")
        st.info("Pour activer la génération automatique du PDF417, installez la bibliothèque sur l'environnement d'exécution :\n\n"
                "`pip install pypdf417 pillow`")
        st.markdown("**Raw AAMVA string (à utiliser pour générer le PDF417 ailleurs)**")
        st.code(raw_string, language="text")
        st.download_button(
            label="Télécharger la chaîne AAMVA (TXT)",
            data=raw_string.encode("utf-8"),
            file_name="aamva_string.txt",
            mime="text/plain"
        )

    st.success("Génération terminée.")
