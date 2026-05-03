import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

# Configuration de la page style "Minimalist Dark Mode"
st.set_page_config(page_title="FLOW | Deep Work", layout="centered")

st.title("🌊 FLOW")
st.subheader("Productivité & Discipline")

# --- SIDEBAR : SAISIE DES DONNÉES ---
st.sidebar.header("Nouvelle Session")
task_name = st.sidebar.text_input("Tâche réalisée")
duration = st.sidebar.slider("Durée (minutes)", 15, 240, 60)
intensity = st.sidebar.select_slider("Intensité (Focus)", options=[1, 2, 3, 4, 5])

if st.sidebar.button("Enregistrer la session"):
    # Ici, on simule une base de données avec un CSV local
    new_data = pd.DataFrame({
        "Date": [datetime.date.today()],
        "Tâche": [task_name],
        "Durée": [duration],
        "Intensité": [intensity],
        "Score": [(duration * intensity) / 10]
    })
    st.sidebar.success("Session enregistrée !")
    # Note : Dans une vraie app, on ajouterait new_data au fichier CSV existant

# --- DASHBOARD PRINCIPAL ---

# Simulation de données pour l'exemple
data = pd.DataFrame({
    "Date": pd.to_datetime(["2023-10-01", "2023-10-02", "2023-10-03", "2023-10-04"]),
    "Score": [45, 30, 85, 60]
})

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Score de Focus Moyen", value="62 pts", delta="+12%")
with col2:
    st.metric(label="Total Deep Work", value="14h", delta="2h today")

# Graphique de progression
st.write("### Ta courbe de progression")
fig = px.line(data, x="Date", y="Score", markers=True, 
              color_discrete_sequence=['#00FFCC']) # Couleur Néon façon Loannlv
fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig)

# --- HABIT TRACKER ---
st.write("### Discipline Quotidienne")
c1, c2, c3 = st.columns(3)
c1.checkbox("Lecture 20min")
c2.checkbox("Entraînement")
c3.checkbox("Méditation")