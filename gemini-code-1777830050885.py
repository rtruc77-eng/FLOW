import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px

# --- CONFIGURATION & STYLE ---
st.set_page_config(page_title="FLOW | Discipline", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('flow_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions 
                 (id INTEGER PRIMARY KEY, date TEXT, task TEXT, duration INTEGER, intensity INTEGER, score REAL)''')
    conn.commit()
    conn.close()

def add_session(task, duration, intensity):
    score = (duration * intensity) / 10
    date = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect('flow_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO sessions (date, task, duration, intensity, score) VALUES (?, ?, ?, ?, ?)",
              (date, task, duration, intensity, score))
    conn.commit()
    conn.close()

init_db()

# --- INTERFACE ---
st.title("🌊 FLOW : Dashboard de Performance")

# Sidebar pour l'ajout
with st.sidebar:
    st.header("⚡ Nouvelle Session")
    task = st.text_input("Nom de la tâche", placeholder="ex: Deep Work Python")
    dur = st.number_input("Durée (min)", min_value=1, value=60)
    inte = st.select_slider("Intensité / Focus", options=[1, 2, 3, 4, 5], value=3)
    
    if st.button("Enregistrer la session", use_container_width=True):
        if task:
            add_session(task, dur, inte)
            st.success("Session validée !")
        else:
            st.error("Donne un nom à la tâche")

# --- RÉCUPÉRATION DES DONNÉES ---
conn = sqlite3.connect('flow_data.db')
df = pd.read_sql_query("SELECT * FROM sessions", conn)
conn.close()

if not df.empty:
    df['date'] = pd.to_datetime(df['date'])
    
    # Filtrer sur les 7 derniers jours
    last_7_days = datetime.now() - timedelta(days=7)
    df_week = df[df['date'] >= last_7_days].sort_values('date')

    # --- METRICS ---
    col1, col2, col3 = st.columns(3)
    total_score = df_week['score'].sum()
    total_hours = df_week['duration'].sum() / 60
    
    col1.metric("Score Hebdo", f"{total_score:.0f} pts")
    col2.metric("Heures Focus", f"{total_hours:.1h} h")
    col3.metric("Intensité Moyenne", f"{df_week['intensity'].mean():.1f} / 5")

    # --- GRAPHIQUE ---
    st.write("### 📈 Analyse de la Semaine")
    # On groupe par date pour avoir un score quotidien cumulé
    daily_df = df_week.groupby('date')['score'].sum().reset_index()
    
    fig = px.area(daily_df, x='date', y='score', 
                  title="Évolution de la Productivité",
                  color_discrete_sequence=['#00d4ff'])
    fig.update_layout(template="plotly_dark", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    # --- LOGS ET MODIFICATIONS ---
    st.write("### 📝 Historique des Sessions")
    edited_df = st.data_editor(df.sort_values('date', ascending=False), 
                               num_rows="dynamic",
                               column_config={
                                   "score": st.column_config.NumberColumn(format="%.1f")
                               })
    
    if st.button("Sauvegarder les modifications"):
        conn = sqlite3.connect('flow_data.db')
        edited_df.to_sql('sessions', conn, if_exists='replace', index=False)
        conn.close()
        st.rerun()

else:
    st.info("Aucune donnée enregistrée. Commence ta première session de Deep Work !")
