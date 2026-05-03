import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px

# --- 1. CONFIGURATION & STYLE (Mode Deep Work) ---
st.set_page_config(page_title="FLOW | OS", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Fond très sombre pour réduire la fatigue visuelle */
    .stApp { background-color: #0B0E14; color: #E2E8F0; }
    
    /* Cartes de métriques style Dashboard F1 */
    div[data-testid="metric-container"] {
        background-color: #151A23; 
        border: 1px solid #2D3748; 
        padding: 20px; 
        border-radius: 8px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    
    /* Boutons d'action : Minimalistes avec accent Néon */
    .stButton>button { 
        border: 1px solid #00E676; 
        color: #00E676; 
        background-color: transparent; 
        transition: all 0.3s ease; 
        width: 100%;
    }
    .stButton>button:hover { 
        background-color: #00E676; 
        color: #000; 
        border-color: #00E676;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. GESTION DE LA BASE DE DONNÉES ---
DB_NAME = "flow_master.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS flow_sessions 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         date TEXT, task TEXT, duration INTEGER, intensity INTEGER, score REAL)''')

def add_session(task, duration, intensity):
    # Le score récompense la durée ET l'intensité exponentiellement
    score = (duration / 60) * (intensity ** 1.5) * 5 
    date_str = datetime.now().strftime("%Y-%m-%d")
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT INTO flow_sessions (date, task, duration, intensity, score) VALUES (?, ?, ?, ?, ?)",
                     (date_str, task, duration, intensity, round(score, 1)))

def get_data():
    with sqlite3.connect(DB_NAME) as conn:
        df = pd.read_sql_query("SELECT * FROM flow_sessions", conn)
    return df

init_db()

# --- 3. INTERFACE UTILISATEUR ---
st.title("⚡ FLOW : Système de Performance")
st.markdown("*Discipline. Focus. Résultats.*")
st.write("---")

# Création des onglets pour une navigation d'application mobile
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🎯 Saisir une Session", "⚙️ Gérer les Données"])

# --- ONGLET 1 : DASHBOARD ---
with tab1:
    df = get_data()
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        # Filtre strict sur les 7 derniers jours
        last_7_days = pd.to_datetime(datetime.now().date() - timedelta(days=7))
        df_week = df[df['date'] >= last_7_days].copy()

        # Calculs (Correction du bug de formatage ici : .1f)
        total_hours = df_week['duration'].sum() / 60
        total_score = df_week['score'].sum()
        avg_intensity = df_week['intensity'].mean() if not df_week.empty else 0

        # Affichage des KPIs
        c1, c2, c3 = st.columns(3)
        c1.metric("Temps Focus (7j)", f"{total_hours:.1f} h")
        c2.metric("Score Deep Work (7j)", f"{total_score:.0f} pts")
        c3.metric("Intensité Moy. (7j)", f"{avg_intensity:.1f} / 5")

        st.write("<br>", unsafe_allow_html=True)
        st.subheader("📈 Évolution de la productivité")
        
        if not df_week.empty:
            # Groupement par jour pour le graphique
            daily_stats = df_week.groupby(df_week['date'].dt.strftime('%Y-%m-%d'))['score'].sum().reset_index()
            
            # Graphique Plotly optimisé
            fig = px.bar(daily_stats, x='date', y='score', text='score',
                         color_discrete_sequence=['#00E676'])
            fig.update_layout(
                template="plotly_dark", 
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Date", 
                yaxis_title="Score de Focus",
                margin=dict(l=0, r=0, t=30, b=0)
            )
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune donnée enregistrée sur les 7 derniers jours.")
    else:
        st.info("Ta base de données est vide. Passe à l'onglet 'Saisir une Session'.")

# --- ONGLET 2 : NOUVELLE SESSION ---
with tab2:
    st.subheader("Enregistrer du Deep Work")
    with st.form("add_session_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        task_name = col_a.text_input("Objectif accompli", placeholder="Ex: Montage vidéo / Code")
        task_duration = col_b.number_input("Durée (minutes)", min_value=5, max_value=480, value=60, step=5)
        
        st.write("Niveau d'intensité")
        task_intensity = st.slider("1 = Distrait | 5 = État de Flow absolu", 1, 5, 4, label_visibility="collapsed")
        
        submitted = st.form_submit_button("🔥 Valider la session")
        
        if submitted:
            if task_name.strip():
                add_session(task_name, task_duration, task_intensity)
                st.success("Session enregistrée ! (Actualise ou change d'onglet pour voir les stats)")
            else:
                st.error("Tu dois donner un nom à ta tâche.")

# --- ONGLET 3 : GESTION (CRUD) ---
with tab3:
    st.subheader("Contrôle de la Base de Données")
    st.write("Double-clique sur une case pour modifier une erreur. Sélectionne la ligne à gauche et appuie sur 'Supprimer' (Delete) pour l'effacer.")
    
    df_edit = get_data()
    if not df_edit.empty:
        # st.data_editor permet de modifier/supprimer en direct
        edited_df = st.data_editor(df_edit, num_rows="dynamic", use_container_width=True, hide_index=True)
        
        if st.button("💾 Sauvegarder les modifications dans la base de données"):
            with sqlite3.connect(DB_NAME) as conn:
                edited_df.to_sql('flow_sessions', conn, if_exists='replace', index=False)
            st.success("Base de données mise à jour !")
    else:
        st.write("Aucune donnée à modifier.")
