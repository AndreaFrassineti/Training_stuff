import sqlite3
import datetime
import pandas as pd
import streamlit as st
import plotly.express as px

# --- CONFIGURAZIONE PAGINA STREAMLIT ---
st.set_page_config(
    page_title="Diario Allenamento Pro",
    page_icon="🏋️‍♂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DB_FILE = "allenamento_diario.db"

# --- INIZIALIZZAZIONE DATABASE ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS esercizi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        categoria TEXT NOT NULL,
        blocco TEXT NOT NULL,
        nome TEXT NOT NULL,
        schema_serie_reps TEXT,
        recupero TEXT,
        note TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS diario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT NOT NULL,
        esercizio_id INTEGER NOT NULL,
        peso_kg REAL NOT NULL,
        note_sessione TEXT,
        FOREIGN KEY(esercizio_id) REFERENCES esercizi(id) ON DELETE CASCADE)''')

    cursor.execute("SELECT COUNT(*) FROM esercizi")
    if cursor.fetchone()[0] == 0:
        esercizi_data = [
            # VOLUME
            ("Volume", "Potenziamento 1", "Addome 12 Libr. + 30'' Planche + 15 Laterali", "2x", "2'", "12 libr. + 30'' planche + 15 laterali"),
            ("Volume", "Potenziamento 1", "Trazioni Zavorrate", "3x10", "1'30''", ""),
            ("Volume", "Potenziamento 1", "Rematori TRX", "4x10", "1'30''", ""),
            ("Volume", "Potenziamento 1", "Flessioni", "4x10", "1'15''", ""),
            ("Volume", "Potenziamento Dita 1", "Critical Force", "2x", "-", ""),
            ("Volume", "Potenziamento 2", "Addome Anelli", "10 + Barchetta 30''", "1'30''", "2 serie"),
            ("Volume", "Potenziamento 2", "Flessioni Inclinata", "4x10", "1'15''", ""),
            ("Volume", "Potenziamento 2", "Trazioni", "3x10", "1'30''", ""),
            ("Volume", "Potenziamento 2", "Military Press", "3x10", "1'", ""),
            ("Volume", "Potenziamento Dita 2", "Back Fing. Curl + Fing. Curl", "5xCed (12)", "1'45''", ""),
            ("Volume", "Potenziamento Dita 2", "Reverse Finger Curl", "4x10-12", "1'30''", ""),
            ("Volume", "Potenziamento Dita 2", "Arcing", "almeno 25'", "-", ""),

            # IPERTROFIA
            ("Ipertrofia", "Potenziamento 1", "Addome 12 Libr. + 30'' Planche + 15 Laterali", "2x", "2'", ""),
            ("Ipertrofia", "Potenziamento 1", "Trazioni Zavorrate", "3x10", "1'30''", ""),
            ("Ipertrofia", "Potenziamento 1", "Rematori TRX", "4x10", "1'30''", ""),
            ("Ipertrofia", "Potenziamento 1", "Flessioni", "4x10", "1'15''", ""),
            ("Ipertrofia", "Potenziamento Dita 1", "Back Fing. Curl + Fing. Curl", "5xCed (12)", "1'45''", ""),
            ("Ipertrofia", "Potenziamento Dita 1", "Reverse Finger Curl", "4x10-12", "1'30''", ""),
            ("Ipertrofia", "Potenziamento Dita 1", "Pinch Grip", "4x 12'' vic. ced", "1'30''", ""),
            ("Ipertrofia", "Potenziamento Dita 1", "Hammer Curl", "3x10", "1'", ""),
            ("Ipertrofia", "Potenziamento 2", "Addome Anelli", "10 + Barchetta 30''", "1'30''", "2 serie"),
            ("Ipertrofia", "Potenziamento 2", "Flessioni Inclinata", "4x7", "1'30''", "Aumenta carichi"),
            ("Ipertrofia", "Potenziamento 2", "Military Press", "3x10", "1'30''", ""),
            ("Ipertrofia", "Potenziamento 2", "Trazioni", "4x7", "1'30''", ""),
            ("Ipertrofia", "Potenziamento Dita 2", "Back Fing. Curl + Fing. Curl", "5xCed (12)", "1'45''", ""),
            ("Ipertrofia", "Potenziamento Dita 2", "Reverse Finger Curl", "4x10-12", "1'30''", ""),
            ("Ipertrofia", "Potenziamento Dita 2", "Arcing", "almeno 20'", "-", ""),

            # FORZA
            ("Forza", "Potenziamento 1", "Trazioni Zavorrate", "3-2-1-2-3", "4'30''", "85%-90%-120%"),
            ("Forza", "Potenziamento 1", "Addome alla Sbarra", "3x8", "2'", ""),
            ("Forza", "Potenziamento Dita 1", "Pinch Grip", "3x 6'' on", "4'", "@90%"),
            ("Forza", "Potenziamento Dita 1", "3 Finger Drag 20mm", "3x 6'' on", "4'", "@90%"),
            ("Forza", "Potenziamento Dita 1", "Bidito 20mm", "3x 6'' on", "4'", "@90%"),
            ("Forza", "Potenziamento 2", "Lock Off Puleggia", "3x (20-90-120) 5s", "4'30''", ""),
            ("Forza", "Potenziamento 2", "Rematori TRX", "2x6", "4'", "@80% max"),
            ("Forza", "Potenziamento 2", "Controlli Front Lever", "3x2", "3'", ""),
            ("Forza", "Potenziamento 2", "Military Press", "3x6", "3'", "Carico elevato"),
            ("Forza", "Potenziamento Dita 2", "Pinch Grip", "1x 6'' on", "4'", "@90%"),
            ("Forza", "Potenziamento Dita 2", "3 Finger Drag 20mm", "3x 6'' on", "4'", "@90%"),
            ("Forza", "Potenziamento Dita 2", "Bidito 20mm", "3x 6'' on", "4'", "@90%"),
        ]
        cursor.executemany("INSERT INTO esercizi (categoria, blocco, nome, schema_serie_reps, recupero, note) VALUES (?, ?, ?, ?, ?, ?)", esercizi_data)

    conn.commit()
    conn.close()

init_db()

# --- FUNZIONI DI UTILITÀ DB ---
def get_esercizi_dict():
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute("SELECT id, nome, categoria, blocco FROM esercizi ORDER BY categoria, blocco, nome").fetchall()
    conn.close()
    return {f"[{r[2]} | {r[3]}] {r[1]}": r[0] for r in rows}

# --- HEADER PRINCIPALE ---
st.title("🏋️‍♂️ Diario Allenamento & Periodizzazione")

# Navigation Tabs (perfetti per touch da mobile)
tab_diario, tab_planning, tab_schede, tab_stats = st.tabs([
    "✏️ Diario Allenamento", 
    "📅 Planning & Fasi", 
    "📋 Schede & Esercizi", 
    "📈 Statistiche Forza"
])

# ==========================================
# TAB 1: DIARIO ALLENAMENTO (In primis per velocizzare in palestra)
# ==========================================
with tab_diario:
    st.subheader("📝 Registra Serie / Esercizio")
    
    esercizi_dict = get_esercizi_dict()
    
    if not esercizi_dict:
        st.warning("Nessun esercizio disponibile. Aggiungine uno nella sezione Schede.")
    else:
        with st.form("form_diario", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                data_val = st.date_input("Data", datetime.date.today())
                ex_sel = st.selectbox("Seleziona Esercizio", options=list(esercizi_dict.keys()))
            with col2:
                carico_val = st.number_input("Carico / Zavorra (kg)", min_value=0.0, step=0.5, format="%.1f")
                note_val = st.text_input("Note Sessione (es. RPE 8, buone sensazioni)")
            
            submit_log = st.form_submit_button("💾 SALVA SERIE", use_container_width=True)
            
            if submit_log:
                conn = sqlite3.connect(DB_FILE)
                conn.execute(
                    "INSERT INTO diario (data, esercizio_id, peso_kg, note_sessione) VALUES (?, ?, ?, ?)",
                    (data_val.strftime("%Y-%m-%d"), esercizi_dict[ex_sel], carico_val, note_val)
                )
                conn.commit()
                conn.close()
                st.success(f"✅ Registrato: {ex_sel} -> {carico_val} kg")

    st.divider()
    st.subheader("📜 Storico Allenamenti")
    
    conn = sqlite3.connect(DB_FILE)
    df_diario = pd.read_sql_query("""
        SELECT d.id, d.data as "Data", e.categoria as "Fase", e.blocco as "Blocco", e.nome as "Esercizio", d.peso_kg as "Peso (kg)", d.note_sessione as "Note"
        FROM diario d 
        JOIN esercizi e ON d.esercizio_id = e.id 
        ORDER BY d.data DESC, d.id DESC
    """, conn)
    conn.close()

    if not df_diario.empty:
        st.dataframe(df_diario.drop(columns=["id"]), use_container_width=True, hide_index=True)
        
        # Possibilità di cancellare una riga sbagliata
        with st.expander("🗑️ Elimina una registrazione errata"):
            id_to_del = st.selectbox("Seleziona ID da eliminare", df_diario["id"].tolist(), format_func=lambda x: f"ID {x} - {df_diario[df_diario['id']==x]['Esercizio'].values[0]} ({df_diario[df_diario['id']==x]['Data'].values[0]})")
            if st.button("Elimina Registrazione", type="primary"):
                conn = sqlite3.connect(DB_FILE)
                conn.execute("DELETE FROM diario WHERE id = ?", (id_to_del,))
                conn.commit()
                conn.close()
                st.rerun()
    else:
        st.info("Ancora nessuna sessione registrata.")

# ==========================================
# TAB 2: PLANNING & FASI
# ==========================================
with tab_planning:
    st.subheader("📌 Calendario Periodizzazione Fasi")
    
    df_fasi = pd.DataFrame([
        {"Fase": "VOLUME 🟠", "Data Inizio": "14 Settembre", "Data Fine": "10 Ottobre"},
        {"Fase": "IPERTROFIA 🔴", "Data Inizio": "12 Ottobre", "Data Fine": "24 Ottobre"},
        {"Fase": "FORZA 🟣", "Data Inizio": "26 Ottobre", "Data Fine": "16 Dicembre"}
    ])
    st.table(df_fasi)

    st.divider()
    st.subheader("🏋️ Scheda dei 3 Giorni di Allenamento")

    fase_scelta = st.radio("Seleziona Fase:", ["VOLUME", "IPERTROFIA", "FORZA"], horizontal=True)

    planning_data = {
        "VOLUME": [
            ("GIORNO 1", "• **Potenziamento 1** (Addome 12 Libr., Trazioni Zav, Rematori TRX, Flessioni)\n\n• **Potenziamento Dita 1** (Critical Force)\n\n• **4x4**"),
            ("GIORNO 2", "• **Riscaldamento**\n\n• **Moonboard** (blocchi facili 26c con mosse challenging)\n\n• **Circuiti**"),
            ("GIORNO 3", "• **Potenziamento 2** (Addome Anelli, Flessioni Inclinata, Trazioni, Military)\n\n• **Potenziamento Dita 2** (Back/Finger Curl, Reverse Curl, Arcing)\n\n• **Corda**")
        ],
        "IPERTROFIA": [
            ("GIORNO 1", "• **Potenziamento 1** (Addome Planche, Trazioni Zav, Rematori TRX, Flessioni)\n\n• **Potenziamento Dita 1** (Finger Curl, Reverse Curl, Pinch Grip, Hammer Curl)"),
            ("GIORNO 2", "• **Riscaldamento & Scalata**\n\n• **Blocchi + Circuiti** ad alta intensità"),
            ("GIORNO 3", "• **Potenziamento 2** (Addome Anelli, Flessioni Inclinati, Military, Trazioni 4x7)\n\n• **Potenziamento Dita 2** (Finger Curl, Reverse Curl, Arcing)")
        ],
        "FORZA": [
            ("GIORNO 1", "• **Potenziamento Forza 1** (Trazioni Zav 3-2-1-2-3 @85-120%, Addome Sbarra)\n\n• **Forza Dita 1** (Pinch Grip @90%, 3 Finger Drag @90%, Bidito @90%)"),
            ("GIORNO 2", "• **Riscaldamento**\n\n• **Lavoro su Blocchi Hard / Progetto**"),
            ("GIORNO 3", "• **Potenziamento Forza 2** (Lock Off Puleggia, Rematori TRX, Front Lever, Military)\n\n• **Forza Dita 2** (Pinch Grip, 3 Finger Drag, Bidito)")
        ]
    }

    giorni = planning_data.get(fase_scelta, [])
    for giorno, desc in giorni:
        with st.expander(f"🔹 **{giorno}**", expanded=True):
            st.markdown(desc)

# ==========================================
# TAB 3: SCHEDE & ESERCIZI
# ==========================================
with tab_schede:
    st.subheader("📋 Consultazione & Gestione Esercizi")

    col_f, col_b = st.columns(2)
    with col_f:
        filter_fase = st.selectbox("Filtra per Fase", ["Tutte", "Volume", "Ipertrofia", "Forza"])
    with col_b:
        filter_blocco = st.selectbox("Filtra per Blocco", ["Tutti", "Potenziamento 1", "Potenziamento Dita 1", "Potenziamento 2", "Potenziamento Dita 2"])

    conn = sqlite3.connect(DB_FILE)
    query = "SELECT id, categoria as Fase, blocco as Blocco, nome as Esercizio, schema_serie_reps as 'Serie/Reps', recupero as Recupero, note as Note FROM esercizi WHERE 1=1"
    params = []
    if filter_fase != "Tutte":
        query += " AND categoria = ?"
        params.append(filter_fase)
    if filter_blocco != "Tutti":
        query += " AND blocco = ?"
        params.append(filter_blocco)
    query += " ORDER BY categoria, blocco, id"

    df_ex = pd.read_sql_query(query, conn, params=params)
    conn.close()

    st.dataframe(df_ex.drop(columns=["id"]), use_container_width=True, hide_index=True)

    with st.expander("➕ Aggiungi un Nuovo Esercizio"):
        with st.form("add_ex_form", clear_on_submit=True):
            fase_in = st.selectbox("Fase", ["Volume", "Ipertrofia", "Forza"])
            blocco_in = st.selectbox("Blocco", ["Potenziamento 1", "Potenziamento Dita 1", "Potenziamento 2", "Potenziamento Dita 2"])
            nome_in = st.text_input("Nome Esercizio")
            schema_in = st.text_input("Serie / Reps")
            rec_in = st.text_input("Recupero")
            note_in = st.text_input("Note")
            
            sub_ex = st.form_submit_button("Salva Esercizio")
            if sub_ex and nome_in:
                conn = sqlite3.connect(DB_FILE)
                conn.execute(
                    "INSERT INTO esercizi (categoria, blocco, nome, schema_serie_reps, recupero, note) VALUES (?, ?, ?, ?, ?, ?)",
                    (fase_in, blocco_in, nome_in, schema_in, rec_in, note_in)
                )
                conn.commit()
                conn.close()
                st.success("Esercizio aggiunto con successo!")
                st.rerun()

# ==========================================
# TAB 4: STATISTICHE FORZA
# ==========================================
with tab_stats:
    st.subheader("📈 Analisi Progressione Carichi")

    esercizi_dict = get_esercizi_dict()
    if esercizi_dict:
        ex_stat_sel = st.selectbox("Scegli Esercizio da Analizzare:", options=list(esercizi_dict.keys()), key="stat_sel")
        
        conn = sqlite3.connect(DB_FILE)
        df_chart = pd.read_sql_query(
            "SELECT data as Data, peso_kg as 'Carico (kg)' FROM diario WHERE esercizio_id = ? ORDER BY data ASC",
            conn, params=(esercizi_dict[ex_stat_sel],)
        )
        conn.close()

        if not df_chart.empty:
            fig = px.line(
                df_chart, x="Data", y="Carico (kg)", 
                markers=True, title=f"Progressione: {ex_stat_sel}",
                template="plotly_dark"
            )
            fig.update_traces(line_color="#00d2ff", line_width=3, marker_size=8)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nessun dato registrato per questo esercizio. Vai nel Diario per registrare il tuo primo allenamento!")