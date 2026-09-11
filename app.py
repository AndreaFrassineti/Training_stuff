import sqlite3
import datetime
import re
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

    # Tabella per i Massimali di Fase (Opzione 1)
    cursor.execute('''CREATE TABLE IF NOT EXISTS massimali (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fase TEXT NOT NULL,
        esercizio_id INTEGER NOT NULL,
        data_test TEXT NOT NULL,
        peso_max_kg REAL NOT NULL,
        note TEXT,
        FOREIGN KEY(esercizio_id) REFERENCES esercizi(id) ON DELETE CASCADE)''')

    cursor.execute("UPDATE esercizi SET categoria = 'Resistenza alla Forza' WHERE categoria = 'Ipertrofia'")

    cursor.execute("SELECT COUNT(*) FROM esercizi")
    if cursor.fetchone()[0] == 0:
        populate_default_exercises(cursor)

    conn.commit()
    conn.close()

def populate_default_exercises(cursor):
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

        # FORZA
        ("Forza", "Potenziamento 1", "Trazioni Zavorrate", "3-2-1-2-3", "4'30''", "85%-90%-120% rest 4'30''"),
        ("Forza", "Potenziamento 1", "Addome alla Sbarra", "3x8", "2'", ""),
        ("Forza", "Potenziamento 1", "Military Press", "3x6", "3'", "Carico altino"),
        ("Forza", "Potenziamento Dita 1", "Pinch Grip", "3x 6'' on", "4'", "@90%"),
        ("Forza", "Potenziamento Dita 1", "Half Crimp 20mm", "3x 6'' on", "4'", "@90%"),
        ("Forza", "Potenziamento 2", "Lock Off Puleggia", "3x (20-90-120) 5s", "4'30''", ""),
        ("Forza", "Potenziamento 2", "Rematori TRX", "2x6", "4'", "@80% max"),
        ("Forza", "Potenziamento 2", "Controlli Front Lever", "3x2", "3'", ""),
        ("Forza", "Potenziamento Dita 2", "Pinch Grip", "3x 6'' on", "4'", "@90%"),
        ("Forza", "Potenziamento Dita 2", "Half Crimp 20mm", "3x 6'' on", "4'", "@90%"),

        # RESISTENZA ALLA FORZA
        ("Resistenza alla Forza", "Potenziamento 1", "Addome 12 Libr. + 30'' Planche + 15 Laterali", "2x", "2'", ""),
        ("Resistenza alla Forza", "Potenziamento 1", "Trazioni Zavorrate", "3x10", "1'30''", ""),
        ("Resistenza alla Forza", "Potenziamento 1", "Rematori TRX", "4x10", "1'30''", ""),
        ("Resistenza alla Forza", "Potenziamento 1", "Flessioni", "4x10", "1'15''", ""),
        ("Resistenza alla Forza", "Potenziamento Dita 1", "Back Fing. Curl + Fing. Curl", "5xCed (12)", "1'45''", ""),
        ("Resistenza alla Forza", "Potenziamento Dita 1", "Reverse Finger Curl", "4x10-12", "1'30''", ""),
        ("Resistenza alla Forza", "Potenziamento Dita 1", "Pinch Grip", "4x 12'' vic. ced", "1'30''", ""),
        ("Resistenza alla Forza", "Potenziamento Dita 1", "Hammer Curl", "3x10", "1'", ""),
        ("Resistenza alla Forza", "Potenziamento 2", "Addome Anelli", "10 + Barchetta 30''", "1'30''", "2 serie"),
        ("Resistenza alla Forza", "Potenziamento 2", "Flessioni Inclinata", "4x7", "1'30''", "Aumenta carichi"),
        ("Resistenza alla Forza", "Potenziamento 2", "Military Press", "3x10", "1'30''", ""),
        ("Resistenza alla Forza", "Potenziamento 2", "Trazioni", "4x7", "1'30''", ""),
        ("Resistenza alla Forza", "Potenziamento Dita 2", "Back Fing. Curl + Fing. Curl", "5xCed (12)", "1'45''", ""),
        ("Resistenza alla Forza", "Potenziamento Dita 2", "Reverse Finger Curl", "4x10-12", "1'30''", ""),
        ("Resistenza alla Forza", "Potenziamento Dita 2", "Arcing", "almeno 20'", "-", ""),
    ]
    cursor.executemany("INSERT INTO esercizi (categoria, blocco, nome, schema_serie_reps, recupero, note) VALUES (?, ?, ?, ?, ?, ?)", esercizi_data)

init_db()

# --- FUNZIONI UTILI ---
def get_esercizi_dict():
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute("SELECT id, nome, categoria, blocco, note FROM esercizi ORDER BY categoria, blocco, nome").fetchall()
    conn.close()
    return {f"[{r[2]} | {r[3]}] {r[1]}": (r[0], r[2], r[4]) for r in rows}

def extract_percentages(text):
    if not text:
        return []
    matches = re.findall(r'(\d+(?:\.\d+)?)\s*%', text)
    return [float(m) for m in matches]

def round_half(val):
    return round(val * 2) / 2

# --- HEADER PRINCIPALE ---
st.title("🏋️‍♂️ Diario Allenamento & Periodizzazione")

tab_diario, tab_massimali, tab_planning, tab_schede, tab_stats = st.tabs([
    "✏️ Diario Allenamento", 
    "🏆 Massimali di Fase",
    "📅 Planning & Fasi", 
    "📋 Schede & Esercizi", 
    "📈 Statistiche Forza"
])

# ==========================================
# TAB 1: DIARIO ALLENAMENTO
# ==========================================
with tab_diario:
    st.subheader("📝 Registra Serie / Esercizio")
    
    esercizi_dict = get_esercizi_dict()
    
    if not esercizi_dict:
        st.warning("Nessun esercizio disponibile. Aggiungine uno nella sezione Schede & Esercizi.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            data_val = st.date_input("Data", datetime.date.today())
            ex_sel_key = st.selectbox("Seleziona Esercizio", options=list(esercizi_dict.keys()))
            ex_id, ex_fase, ex_note = esercizi_dict[ex_sel_key]

            # Recupero Massimale per questo esercizio (se registrato)
            conn = sqlite3.connect(DB_FILE)
            res_max = conn.execute(
                "SELECT peso_max_kg, data_test FROM massimali WHERE esercizio_id = ? ORDER BY data_test DESC LIMIT 1",
                (ex_id,)
            ).fetchone()
            conn.close()

            calculated_carico = 0.0
            pcts = extract_percentages(ex_note)

            if res_max:
                max_val = res_max[0]
                st.info(f"💡 Massimale registrato per questo esercizio: **{max_val} kg** (Test del {res_max[1]})")
                
                if pcts:
                    st.markdown("**Calcolo Target da Percentuali Nota:**")
                    cols_pct = st.columns(len(pcts))
                    for idx, p in enumerate(pcts):
                        target_kg = round_half(max_val * (p / 100.0))
                        with cols_pct[idx]:
                            if st.button(f"{p:.0f}% -> {target_kg} kg", key=f"btn_pct_{idx}"):
                                st.session_state["carico_input"] = float(target_kg)
            else:
                st.caption("ℹ️ Nessun massimale registrato per questo esercizio. Inseriscilo nel tab *🏆 Massimali di Fase* per il calcolo automatico.")

        with col2:
            default_peso = st.session_state.get("carico_input", 0.0)
            carico_val = st.number_input("Carico / Zavorra (kg)", min_value=0.0, step=0.5, value=default_peso, format="%.1f")
            note_val = st.text_input("Note Sessione (es. RPE 8, buone sensazioni)")
            
            if st.button("💾 SALVA SERIE", use_container_width=True, type="primary"):
                conn = sqlite3.connect(DB_FILE)
                conn.execute(
                    "INSERT INTO diario (data, esercizio_id, peso_kg, note_sessione) VALUES (?, ?, ?, ?)",
                    (data_val.strftime("%Y-%m-%d"), ex_id, carico_val, note_val)
                )
                conn.commit()
                conn.close()
                st.success(f"✅ Registrato: {ex_sel_key} -> {carico_val} kg")

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
# TAB 2: MASSIMALI DI FASE (NUOVO MODULO)
# ==========================================
with tab_massimali:
    st.subheader("🏆 Registrazione & Calcolo Massimali di Fase")
    st.write("Inserisci i risultati dei test massimali (1RM / Max Zavorra) eseguiti ad inizio fase. Il sistema calcolerà automaticamente i carichi target per le percentuali richieste.")

    col_m1, col_m2 = st.columns([1, 1])

    with col_m1:
        st.markdown("##### ➕ Registra Nuovo Massimale Testato")
        esercizi_dict = get_esercizi_dict()
        
        if esercizi_dict:
            with st.form("form_massimale", clear_on_submit=True):
                fase_test = st.selectbox("Fase del Test", ["Volume", "Forza", "Resistenza alla Forza"])
                ex_m_sel = st.selectbox("Esercizio Testato", options=list(esercizi_dict.keys()))
                data_m = st.date_input("Data Test", datetime.date.today())
                peso_max = st.number_input("Massimale Raggiunto (kg)", min_value=0.0, step=0.5, format="%.1f")
                note_m = st.text_input("Note (es. sospensione 5s, zavorra 1RM)")

                sub_m = st.form_submit_button("💾 Salva Massimale", use_container_width=True)
                if sub_m and peso_max > 0:
                    ex_id_m = esercizi_dict[ex_m_sel][0]
                    conn = sqlite3.connect(DB_FILE)
                    conn.execute(
                        "INSERT INTO massimali (fase, esercizio_id, data_test, peso_max_kg, note) VALUES (?, ?, ?, ?, ?)",
                        (fase_test, ex_id_m, data_m.strftime("%Y-%m-%d"), peso_max, note_m)
                    )
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Massimale salvato: {peso_max} kg per {ex_m_sel}")
                    st.rerun()

    with col_m2:
        st.markdown("##### 📊 Tabella Conversioni Percentuali dinamiche")
        conn = sqlite3.connect(DB_FILE)
        df_m_list = pd.read_sql_query("""
            SELECT m.id, m.fase as "Fase", e.nome as "Esercizio", m.peso_max_kg as "1RM (kg)", m.data_test as "Data Test"
            FROM massimali m
            JOIN esercizi e ON m.esercizio_id = e.id
            ORDER BY m.data_test DESC
        """, conn)
        conn.close()

        if not df_m_list.empty:
            sel_m_id = st.selectbox(
                "Seleziona Massimale da Calcolare", 
                df_m_list["id"].tolist(),
                format_func=lambda x: f"{df_m_list[df_m_list['id']==x]['Esercizio'].values[0]} ({df_m_list[df_m_list['id']==x]['Fase'].values[0]}) - {df_m_list[df_m_list['id']==x]['1RM (kg)'].values[0]} kg"
            )
            
            row_sel = df_m_list[df_m_list['id'] == sel_m_id].iloc[0]
            val_1rm = row_sel["1RM (kg)"]
            
            # Tabella percentuali dinamiche
            pct_list = [50, 60, 70, 75, 80, 85, 90, 95, 100, 120]
            calc_data = [{"% Massimale": f"{p}%", "Carico Calcolato (kg)": round_half(val_1rm * (p / 100.0))} for p in pct_list]
            st.dataframe(pd.DataFrame(calc_data), use_container_width=True, hide_index=True)
        else:
            st.info("Nessun massimale ancora salvato.")

    st.divider()
    st.subheader("📋 Storico Massimali Registrati")
    if not df_m_list.empty:
        st.dataframe(df_m_list.drop(columns=["id"]), use_container_width=True, hide_index=True)
        
        with st.expander("🗑️ Elimina Massimale"):
            m_del_id = st.selectbox("Seleziona ID Massimale da Eliminare", df_m_list["id"].tolist(), format_func=lambda x: f"ID {x} - {df_m_list[df_m_list['id']==x]['Esercizio'].values[0]}")
            if st.button("Elimina Massimale", type="primary"):
                conn = sqlite3.connect(DB_FILE)
                conn.execute("DELETE FROM massimali WHERE id = ?", (m_del_id,))
                conn.commit()
                conn.close()
                st.success("Massimale eliminato!")
                st.rerun()

# ==========================================
# TAB 3: PLANNING & FASI
# ==========================================
with tab_planning:
    st.subheader("📌 Calendario Periodizzazione Fasi")
    
    df_fasi = pd.DataFrame([
        {"Fase": "VOLUME 🟠", "Periodo": "14 Settembre - 5 Ottobre", "Note": "Segue Settimana di Scarico ⬇️"},
        {"Fase": "FORZA 🟣", "Periodo": "12 Ottobre - 8 Novembre", "Note": "Segue Settimana di Scarico ⬇️"},
        {"Fase": "RESISTENZA ALLA FORZA 🔴", "Periodo": "16 Novembre - 12 Dicembre", "Note": "Poche rep, fatte bene"}
    ])
    st.table(df_fasi)

    st.divider()
    st.subheader("🏋️ Scheda dei 3 Giorni di Allenamento")

    fase_scelta = st.radio("Seleziona Fase:", ["VOLUME", "FORZA", "RESISTENZA ALLA FORZA"], horizontal=True)

    planning_data = {
        "VOLUME": [
            ("GIORNO 1", "- **Potenziamento 1** (Addome 12 Libr., Trazioni Zav, Rematori TRX, Flessioni)\n- **Potenziamento Dita 1** (Critical Force)\n- **4x4**"),
            ("GIORNO 2", "- **Riscaldamento**\n- **Moonboard** (blocchi facili 26c con mosse challenging)\n- **8 Vie 6A -> 6C**"),
            ("GIORNO 3", "- **Potenziamento 2** (Addome Anelli, Flessioni Inclinata, Trazioni, Military)\n- **Potenziamento Dita 2** (Back/Finger Curl, Reverse Curl, Arcing)\n- **Circuiti**")
        ],
        "FORZA": [
            ("GIORNO 1", "- **Potenziamento 1** (Trazioni Zav 3-2-1-2-3 @85-120%, Addome Sbarra, Military Press)\n- **Forza Dita 1** (Pinch Grip @90%, Half Crimp 20mm @90%)\n- **Blocchi al limite** (6 min. rest)"),
            ("GIORNO 2", "- **Riscaldamento**\n- **Moonboard** (blocchi al limite - 6 min rest)"),
            ("GIORNO 3", "- **Potenziamento 2** (Lock Off Puleggia, Rematori TRX, Front Lever)\n- **Forza Dita 2** (Pinch Grip @90%, Half Crimp 20mm @90%)\n- **3x3 con giubbotto** (2 min rest. + 6 min rest.)")
        ],
        "RESISTENZA ALLA FORZA": [
            ("GIORNO 1", "- **Potenziamento 1** (Addome Planche, Trazioni Zav, Rematori TRX, Flessioni / Finger Curl, Reverse Curl, Pinch Grip, Hammer Curl)\n- **Blocchi a gruppi di 2** (poche rep, fatte bene)"),
            ("GIORNO 2", "- **Riscaldamento**\n- **Moonboard** (3 blocchi da fare di fila. Pausa 8 min - 5 rep.)"),
            ("GIORNO 3", "- **Potenziamento 2** (Addome Anelli, Flessioni Inclinati, Military, Trazioni 4x7 / Finger Curl, Reverse Curl, Arcing)\n- **3/4 Vie al limite** (20/30 min rest.)")
        ]
    }

    giorni = planning_data.get(fase_scelta, [])
    for giorno, desc in giorni:
        with st.expander(f"🔹 **{giorno}**", expanded=True):
            st.markdown(desc)

# ==========================================
# TAB 4: SCHEDE & GESTIONE ESERCIZI
# ==========================================
with tab_schede:
    st.subheader("📋 Consultazione & Gestione Esercizi")

    conn = sqlite3.connect(DB_FILE)
    fasi_disponibili = ["Tutte"] + [r[0] for r in conn.execute("SELECT DISTINCT categoria FROM esercizi ORDER BY categoria").fetchall()]
    blocchi_disponibili = ["Tutti"] + [r[0] for r in conn.execute("SELECT DISTINCT blocco FROM esercizi ORDER BY blocco").fetchall()]
    conn.close()

    col_f, col_b = st.columns(2)
    with col_f:
        filter_fase = st.selectbox("Filtra per Fase", fasi_disponibili)
    with col_b:
        filter_blocco = st.selectbox("Filtra per Blocco", blocchi_disponibili)

    conn = sqlite3.connect(DB_FILE)
    query = "SELECT id as ID, categoria as Fase, blocco as Blocco, nome as Esercizio, schema_serie_reps as 'Serie/Reps', recupero as Recupero, note as Note FROM esercizi WHERE 1=1"
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

    st.dataframe(df_ex, use_container_width=True, hide_index=True)

    st.divider()

    col_add, col_edit, col_del = st.tabs(["➕ Aggiungi Esercizio", "✏️ Modifica Esercizio", "🗑️ Elimina Esercizio"])

    # 1. AGGIUNGI ESERCIZIO
    with col_add:
        with st.form("add_ex_form", clear_on_submit=True):
            st.markdown("##### Inserisci un nuovo esercizio nel database")
            fase_in = st.selectbox("Fase", ["Volume", "Forza", "Resistenza alla Forza"])
            blocco_in = st.selectbox("Blocco", ["Potenziamento 1", "Potenziamento Dita 1", "Potenziamento 2", "Potenziamento Dita 2"])
            nome_in = st.text_input("Nome Esercizio")
            schema_in = st.text_input("Serie / Reps (es. 3x10, 3-2-1-2-3)")
            rec_in = st.text_input("Recupero (es. 1'30'', 4')")
            note_in = st.text_input("Note (es. @90%, zavorra, ecc.)")
            
            sub_ex = st.form_submit_button("➕ Salva Nuovo Esercizio", use_container_width=True)
            if sub_ex:
                if nome_in.strip():
                    conn = sqlite3.connect(DB_FILE)
                    conn.execute(
                        "INSERT INTO esercizi (categoria, blocco, nome, schema_serie_reps, recupero, note) VALUES (?, ?, ?, ?, ?, ?)",
                        (fase_in, blocco_in, nome_in.strip(), schema_in.strip(), rec_in.strip(), note_in.strip())
                    )
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Esercizio '{nome_in}' aggiunto con successo!")
                    st.rerun()
                else:
                    st.error("Inserisci il nome dell'esercizio.")

    # 2. MODIFICA ESERCIZIO
    with col_edit:
        conn = sqlite3.connect(DB_FILE)
        all_ex = conn.execute("SELECT id, categoria, blocco, nome, schema_serie_reps, recupero, note FROM esercizi ORDER BY categoria, blocco, nome").fetchall()
        conn.close()

        if all_ex:
            ex_options = {f"ID {r[0]} - [{r[1]} | {r[2]}] {r[3]}": r for r in all_ex}
            selected_ex_label = st.selectbox("Seleziona Esercizio da Modificare", list(ex_options.keys()))
            selected_ex = ex_options[selected_ex_label]

            with st.form("edit_ex_form"):
                st.markdown(f"##### Modifica Esercizio: {selected_ex[3]}")
                
                fases = ["Volume", "Forza", "Resistenza alla Forza"]
                idx_fase = fases.index(selected_ex[1]) if selected_ex[1] in fases else 0
                edit_fase = st.selectbox("Fase", fases, index=idx_fase)
                
                blocchi = ["Potenziamento 1", "Potenziamento Dita 1", "Potenziamento 2", "Potenziamento Dita 2"]
                idx_blocco = blocchi.index(selected_ex[2]) if selected_ex[2] in blocchi else 0
                edit_blocco = st.selectbox("Blocco", blocchi, index=idx_blocco)
                
                edit_nome = st.text_input("Nome Esercizio", value=selected_ex[3])
                edit_schema = st.text_input("Serie / Reps", value=selected_ex[4] if selected_ex[4] else "")
                edit_rec = st.text_input("Recupero", value=selected_ex[5] if selected_ex[5] else "")
                edit_note = st.text_input("Note", value=selected_ex[6] if selected_ex[6] else "")

                sub_edit = st.form_submit_button("💾 Salva Modifiche", use_container_width=True)
                if sub_edit:
                    conn = sqlite3.connect(DB_FILE)
                    conn.execute("""
                        UPDATE esercizi 
                        SET categoria = ?, blocco = ?, nome = ?, schema_serie_reps = ?, recupero = ?, note = ?
                        WHERE id = ?
                    """, (edit_fase, edit_blocco, edit_nome, edit_schema, edit_rec, edit_note, selected_ex[0]))
                    conn.commit()
                    conn.close()
                    st.success("✅ Esercizio aggiornato con successo!")
                    st.rerun()

    # 3. ELIMINA ESERCIZIO
    with col_del:
        conn = sqlite3.connect(DB_FILE)
        all_ex = conn.execute("SELECT id, categoria, blocco, nome FROM esercizi ORDER BY categoria, blocco, nome").fetchall()
        conn.close()

        if all_ex:
            ex_del_options = {f"ID {r[0]} - [{r[1]} | {r[2]}] {r[3]}": r[0] for r in all_ex}
            selected_del_label = st.selectbox("Seleziona Esercizio da Eliminare", list(ex_del_options.keys()))
            
            if st.button("🗑️ Elimina Definitivamente", type="primary", use_container_width=True):
                ex_id_to_del = ex_del_options[selected_del_label]
                conn = sqlite3.connect(DB_FILE)
                conn.execute("DELETE FROM esercizi WHERE id = ?", (ex_id_to_del,))
                conn.commit()
                conn.close()
                st.success("✅ Esercizio eliminato!")
                st.rerun()

    with st.expander("🔄 Ripristina / Reset Esercizi Predefiniti"):
        st.write("Se desideri ripristinare la tabella degli esercizi al piano originale, clicca sul pulsante sottostante.")
        if st.button("🔄 Ripristina Schede Predefinite"):
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM esercizi")
            populate_default_exercises(cursor)
            conn.commit()
            conn.close()
            st.success("✅ Schede ripristinate ai valori predefiniti!")
            st.rerun()

# ==========================================
# TAB 5: STATISTICHE FORZA
# ==========================================
with tab_stats:
    st.subheader("📈 Analisi Progressione Carichi")

    esercizi_dict = get_esercizi_dict()
    if esercizi_dict:
        ex_stat_sel = st.selectbox("Scegli Esercizio da Analizzare:", options=list(esercizi_dict.keys()), key="stat_sel")
        ex_stat_id = esercizi_dict[ex_stat_sel][0]
        
        conn = sqlite3.connect(DB_FILE)
        df_chart = pd.read_sql_query(
            "SELECT data as Data, peso_kg as 'Carico (kg)' FROM diario WHERE esercizio_id = ? ORDER BY data ASC",
            conn, params=(ex_stat_id,)
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