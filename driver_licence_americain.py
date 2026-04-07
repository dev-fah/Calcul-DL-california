import streamlit as st
import datetime

st.set_page_config(page_title="Permis réaliste", layout="centered")

# -------------------------
# CSS
# -------------------------
st.markdown("""
<style>
.card {
    width: 420px;
    border-radius: 14px;
    padding: 16px;
    background: linear-gradient(135deg,#1e3a8a,#2563eb);
    color: white;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    margin: auto;
    font-family: Arial, sans-serif;
}
.header {
    display:flex;
    justify-content:space-between;
    font-weight:700;
    margin-bottom:10px;
    font-size:14px;
}
.body { 
    display:flex; 
    gap:12px; 
}
.photo {
    width:90px;
    height:110px;
    background:#e5e7eb;
    border-radius:8px;
}
.info { 
    flex:1; 
    font-size:12px; 
}
.label { 
    opacity:0.7;
    font-size:10px; 
    margin-top:6px;
}
.value { 
    font-weight:700;
    margin-bottom:4px; 
}
.badge {
    background:white;
    color:#1e3a8a;
    padding:2px 6px;
    border-radius:6px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Carte
# -------------------------
st.markdown("""
<div class="card">
    <div class="header">
        <div>CALIFORNIA DL</div>
        <div class="badge">I69193548</div>
    </div>

    <div class="body">
        <div class="photo"></div>

        <div class="info">
            <div class="label">Nom</div>
            <div class="value">HARMS ROSA</div>

            <div class="label">Sexe</div>
            <div class="value">M</div>

            <div class="label">DOB</div>
            <div class="value">03/15/1995</div>

            <div class="label">OFFICE</div>
            <div class="value">Baie de San Francisco — Corte Madera (525)</div>

            <div class="label">DD</div>
            <div class="value">04/07/202552512FD/25</div>

            <div class="label">ISS / EXP</div>
            <div class="value">04/07/2025 / 03/15/2030</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
