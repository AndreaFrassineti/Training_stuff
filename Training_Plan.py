import sqlite3
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox

DB_FILE = "allenamento_diario.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Crea la tabella degli esercizi con il campo 'blocco'
    cursor.execute('''CREATE TABLE IF NOT EXISTS esercizi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        categoria TEXT NOT NULL,
        blocco TEXT NOT NULL,
        nome TEXT NOT NULL,
        schema_serie_reps TEXT,
        recupero TEXT,
        note TEXT)''')

    # Controllo migrazione nel caso di database preesistente
    cursor.execute("PRAGMA table_info(esercizi)")
    cols = [col[1] for col in cursor.fetchall()]
    if "blocco" not in cols:
        cursor.execute("DROP TABLE IF EXISTS diario")
        cursor.execute("DROP TABLE IF EXISTS esercizi")
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


class FitnessTrackerApp(tb.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Diario Allenamento & Periodizzazione Pro")
        self.geometry("1150x800")

        plt.style.use('dark_background')

        init_db()

        self.notebook = tb.Notebook(self, bootstyle="info")
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.tab_planning = tb.Frame(self.notebook)
        self.tab_schede = tb.Frame(self.notebook)
        self.tab_diario = tb.Frame(self.notebook)
        self.tab_stats = tb.Frame(self.notebook)

        self.notebook.add(self.tab_planning, text=" 📅 Planning & Fasi ")
        self.notebook.add(self.tab_schede, text=" 📋 Schede & Esercizi ")
        self.notebook.add(self.tab_diario, text=" ✏️ Diario Allenamento ")
        self.notebook.add(self.tab_stats, text=" 📈 Statistiche Forza ")

        self.build_tab_planning()
        self.build_tab_schede()
        self.build_tab_diario()
        self.build_tab_stats()

    # --- TAB 0: PLANNING & FASI ---
    def build_tab_planning(self):
        frame_fasi = tb.Labelframe(self.tab_planning, text=" 📌 Periodizzazione Fasi ", padding=15, bootstyle="primary")
        frame_fasi.pack(fill=X, padx=15, pady=10)

        cols_fasi = ("fase", "inizio", "fine")
        tree_fasi = tb.Treeview(frame_fasi, columns=cols_fasi, show="headings", height=3, bootstyle="primary")
        tree_fasi.heading("fase", text="Fase")
        tree_fasi.heading("inizio", text="Data Inizio")
        tree_fasi.heading("fine", text="Data Fine")
        
        tree_fasi.column("fase", anchor=CENTER, width=150)
        tree_fasi.column("inizio", anchor=CENTER, width=150)
        tree_fasi.column("fine", anchor=CENTER, width=150)

        dati_fasi = [
            ("VOLUME 🟠", "14 Settembre", "10 Ottobre"),
            ("IPERTROFIA 🔴", "12 Ottobre", "24 Ottobre"),
            ("FORZA 🟣", "26 Ottobre", "16 Dicembre")
        ]
        for row in dati_fasi:
            tree_fasi.insert("", END, values=row)
        tree_fasi.pack(fill=X)

        frame_settimana = tb.Labelframe(self.tab_planning, text=" 🏋️ Struttura Settimanale (3 Giorni di Allenamento) ", padding=15, bootstyle="info")
        frame_settimana.pack(fill=BOTH, expand=True, padx=15, pady=10)

        frame_selector = tb.Frame(frame_settimana)
        frame_selector.pack(fill=X, pady=(0, 10))

        tb.Label(frame_selector, text="Seleziona Fase:", font=("Helvetica", 11, "bold")).pack(side=LEFT, padx=5)
        self.combo_fase_plan = tb.Combobox(frame_selector, state="readonly", bootstyle="info", width=20)
        self.combo_fase_plan['values'] = ["VOLUME", "IPERTROFIA", "FORZA"]
        self.combo_fase_plan.current(0)
        self.combo_fase_plan.pack(side=LEFT, padx=5)
        self.combo_fase_plan.bind("<<ComboboxSelected>>", lambda e: self.mostra_planning_fase())

        self.container_giorni = tb.Frame(frame_settimana)
        self.container_giorni.pack(fill=BOTH, expand=True)

        self.planning_data = {
            "VOLUME": [
                ("GIORNO 1", "• Potenziamento 1 (Addome, Trazioni Zav, Rematori TRX, Flessioni)\n• Potenziamento Dita 1 (Critical Force)\n• 4x4"),
                ("GIORNO 2", "• Riscaldamento\n• Moonboard (blocchi facili 26c con mosse challenging)\n• Circuiti"),
                ("GIORNO 3", "• Potenziamento 2 (Addome Anelli, Flessioni Inclinata, Trazioni, Military)\n• Potenziamento Dita 2 (Back/Finger Curl, Reverse Curl, Arcing)\n• Corda")
            ],
            "IPERTROFIA": [
                ("GIORNO 1", "• Potenziamento 1 (Addome Planche, Trazioni Zav, Rematori TRX, Flessioni)\n• Potenziamento Dita 1 (Finger Curl, Reverse Curl, Pinch Grip, Hammer Curl)"),
                ("GIORNO 2", "• Riscaldamento & Scalata\n• Blocchi + Circuiti ad alta intensità"),
                ("GIORNO 3", "• Potenziamento 2 (Addome Anelli, Flessioni Inclinati, Military, Trazioni 4x7)\n• Potenziamento Dita 2 (Finger Curl, Reverse Curl, Arcing)")
            ],
            "FORZA": [
                ("GIORNO 1", "• Potenziamento Forza 1 (Trazioni Zav 3-2-1-2-3, Addome Sbarra)\n• Forza Dita 1 (Pinch Grip @90%, 3 Finger Drag @90%, Bidito @90%)"),
                ("GIORNO 2", "• Riscaldamento\n• Lavoro su Blocchi Hard / Progetto"),
                ("GIORNO 3", "• Potenziamento Forza 2 (Lock Off Puleggia, Rematori TRX, Front Lever, Military Press)\n• Forza Dita 2 (Pinch Grip, 3 Finger Drag, Bidito)")
            ]
        }

        self.mostra_planning_fase()

    def mostra_planning_fase(self):
        for widget in self.container_giorni.winfo_children():
            widget.destroy()

        fase_scelta = self.combo_fase_plan.get()
        giorni = self.planning_data.get(fase_scelta, [])

        for giorno, descrizione in giorni:
            card = tb.Labelframe(self.container_giorni, text=f" {giorno} ", padding=12, bootstyle="secondary")
            card.pack(fill=X, pady=6)
            tb.Label(card, text=descrizione, font=("Helvetica", 10), justify=LEFT).pack(anchor=W)

    # --- TAB 1: SCHEDE ED ESERCIZI ---
    def build_tab_schede(self):
        frame_top_filter = tb.Frame(self.tab_schede, padding=10)
        frame_top_filter.pack(fill=X)

        tb.Label(frame_top_filter, text="Filtra per Fase:", font=("Helvetica", 10, "bold")).pack(side=LEFT, padx=(5, 2))
        self.filter_fase = tb.Combobox(frame_top_filter, state="readonly", bootstyle="info", width=15)
        self.filter_fase['values'] = ["Tutte", "Volume", "Ipertrofia", "Forza"]
        self.filter_fase.current(0)
        self.filter_fase.pack(side=LEFT, padx=(0, 15))
        self.filter_fase.bind("<<ComboboxSelected>>", lambda e: self.carica_esercizi())

        tb.Label(frame_top_filter, text="Filtra per Blocco:", font=("Helvetica", 10, "bold")).pack(side=LEFT, padx=(5, 2))
        self.filter_blocco = tb.Combobox(frame_top_filter, state="readonly", bootstyle="info", width=22)
        self.filter_blocco['values'] = ["Tutti", "Potenziamento 1", "Potenziamento Dita 1", "Potenziamento 2", "Potenziamento Dita 2"]
        self.filter_blocco.current(0)
        self.filter_blocco.pack(side=LEFT, padx=(0, 15))
        self.filter_blocco.bind("<<ComboboxSelected>>", lambda e: self.carica_esercizi())

        frame_left = tb.Frame(self.tab_schede, padding=10)
        frame_left.pack(side=LEFT, fill=BOTH, expand=True)

        columns = ("id", "categoria", "blocco", "nome", "schema", "recupero", "note")
        self.tree_esercizi = tb.Treeview(frame_left, columns=columns, show="headings", bootstyle="info")
        
        headers = [("id", "ID", 40), ("categoria", "Fase", 90), ("blocco", "Blocco Potenziamento", 150),
                   ("nome", "Esercizio", 180), ("schema", "Serie/Reps", 110), ("recupero", "Recupero", 80), ("note", "Note", 120)]
        
        for col, text, width in headers:
            self.tree_esercizi.heading(col, text=text)
            self.tree_esercizi.column(col, width=width, anchor=CENTER if col in ("id", "recupero") else W)
        
        self.tree_esercizi.pack(fill=BOTH, expand=True)

        frame_right = tb.Labelframe(self.tab_schede, text=" Gestisci Esercizio ", padding=15, bootstyle="primary")
        frame_right.pack(side=RIGHT, fill=Y, padx=10, pady=10)

        tb.Label(frame_right, text="Fase:", font=("Helvetica", 10)).pack(anchor=W, pady=(5, 2))
        self.entry_cat = tb.Combobox(frame_right, values=["Volume", "Ipertrofia", "Forza"], state="readonly")
        self.entry_cat.current(0)
        self.entry_cat.pack(fill=X)

        tb.Label(frame_right, text="Blocco Potenziamento:", font=("Helvetica", 10)).pack(anchor=W, pady=(10, 2))
        self.entry_blocco = tb.Combobox(frame_right, values=["Potenziamento 1", "Potenziamento Dita 1", "Potenziamento 2", "Potenziamento Dita 2"], state="readonly")
        self.entry_blocco.current(0)
        self.entry_blocco.pack(fill=X)

        tb.Label(frame_right, text="Nome Esercizio:", font=("Helvetica", 10)).pack(anchor=W, pady=(10, 2))
        self.entry_nome = tb.Entry(frame_right, width=28)
        self.entry_nome.pack(fill=X)

        tb.Label(frame_right, text="Serie / Reps:", font=("Helvetica", 10)).pack(anchor=W, pady=(10, 2))
        self.entry_schema = tb.Entry(frame_right, width=28)
        self.entry_schema.pack(fill=X)

        tb.Label(frame_right, text="Recupero:", font=("Helvetica", 10)).pack(anchor=W, pady=(10, 2))
        self.entry_rec = tb.Entry(frame_right, width=28)
        self.entry_rec.pack(fill=X)

        tb.Label(frame_right, text="Note:", font=("Helvetica", 10)).pack(anchor=W, pady=(10, 2))
        self.entry_note = tb.Entry(frame_right, width=28)
        self.entry_note.pack(fill=X)

        tb.Button(frame_right, text="➕ Salva / Aggiungi", bootstyle="success", command=self.salva_esercizio).pack(fill=X, pady=(20, 5))
        tb.Button(frame_right, text="🗑️ Elimina Selezionato", bootstyle="danger-outline", command=self.elimina_esercizio).pack(fill=X)

        self.carica_esercizi()

    def carica_esercizi(self):
        self.tree_esercizi.delete(*self.tree_esercizi.get_children())
        fase_sel = self.filter_fase.get()
        blocco_sel = self.filter_blocco.get()

        query = "SELECT id, categoria, blocco, nome, schema_serie_reps, recupero, note FROM esercizi WHERE 1=1"
        params = []

        if fase_sel != "Tutte":
            query += " AND categoria = ?"
            params.append(fase_sel)
        if blocco_sel != "Tutti":
            query += " AND blocco = ?"
            params.append(blocco_sel)

        query += " ORDER BY categoria, blocco, id"

        conn = sqlite3.connect(DB_FILE)
        for row in conn.execute(query, params):
            self.tree_esercizi.insert("", END, values=row)
        conn.close()

    def salva_esercizio(self):
        cat = self.entry_cat.get().strip()
        blocco = self.entry_blocco.get().strip()
        nome = self.entry_nome.get().strip()
        schema = self.entry_schema.get().strip()
        rec = self.entry_rec.get().strip()
        note = self.entry_note.get().strip()

        if not cat or not blocco or not nome:
            messagebox.showerror("Errore", "Fase, Blocco e Nome Esercizio sono obbligatori.")
            return

        conn = sqlite3.connect(DB_FILE)
        conn.execute("INSERT INTO esercizi (categoria, blocco, nome, schema_serie_reps, recupero, note) VALUES (?, ?, ?, ?, ?, ?)",
                     (cat, blocco, nome, schema, rec, note))
        conn.commit()
        conn.close()
        self.carica_esercizi()
        self.aggiorna_combo_diario()

        self.entry_nome.delete(0, END)
        self.entry_schema.delete(0, END)
        self.entry_rec.delete(0, END)
        self.entry_note.delete(0, END)

    def elimina_esercizio(self):
        selected = self.tree_esercizi.selection()
        if not selected: return
        ex_id = self.tree_esercizi.item(selected[0])["values"][0]
        conn = sqlite3.connect(DB_FILE)
        conn.execute("DELETE FROM esercizi WHERE id = ?", (ex_id,))
        conn.commit()
        conn.close()
        self.carica_esercizi()
        self.aggiorna_combo_diario()

    # --- TAB 2: DIARIO ---
    def build_tab_diario(self):
        frame_input = tb.Labelframe(self.tab_diario, text=" Registra Nuova Sessione ", padding=20, bootstyle="info")
        frame_input.pack(fill=X, padx=10, pady=10)

        tb.Label(frame_input, text="Data (YYYY-MM-DD):").grid(row=0, column=0, sticky=W, pady=5, padx=5)
        self.entry_data = tb.Entry(frame_input, bootstyle="info")
        self.entry_data.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.entry_data.grid(row=0, column=1, sticky=EW, pady=5, padx=5)

        tb.Label(frame_input, text="Esercizio:").grid(row=1, column=0, sticky=W, pady=5, padx=5)
        self.combo_esercizi = tb.Combobox(frame_input, state="readonly", bootstyle="info")
        self.combo_esercizi.grid(row=1, column=1, sticky=EW, pady=5, padx=5)

        tb.Label(frame_input, text="Carico (kg):").grid(row=0, column=2, sticky=W, pady=5, padx=20)
        self.entry_peso = tb.Entry(frame_input, bootstyle="success")
        self.entry_peso.grid(row=0, column=3, sticky=EW, pady=5)

        tb.Label(frame_input, text="Note Sessione:").grid(row=1, column=2, sticky=W, pady=5, padx=20)
        self.entry_note_sessione = tb.Entry(frame_input)
        self.entry_note_sessione.grid(row=1, column=3, sticky=EW, pady=5)

        frame_input.columnconfigure(1, weight=1)
        frame_input.columnconfigure(3, weight=1)

        tb.Button(frame_input, text="📝 Registra Allenamento", bootstyle="success", command=self.salva_diario).grid(row=2, column=0, columnspan=4, pady=15)

        frame_historico = tb.Labelframe(self.tab_diario, text=" Storico Sessioni ", padding=10, bootstyle="secondary")
        frame_historico.pack(fill=BOTH, expand=True, padx=10, pady=5)

        cols = ("id", "data", "esercizio", "peso", "note")
        self.tree_diario = tb.Treeview(frame_historico, columns=cols, show="headings", bootstyle="secondary")
        for col, text in zip(cols, ["ID", "Data", "Esercizio (Fase | Blocco)", "Peso (kg)", "Note Sessione"]):
            self.tree_diario.heading(col, text=text)
        self.tree_diario.column("id", width=40, anchor=CENTER)
        self.tree_diario.column("data", width=100, anchor=CENTER)
        self.tree_diario.column("esercizio", width=350, anchor=W)
        self.tree_diario.column("peso", width=90, anchor=CENTER)
        self.tree_diario.pack(fill=BOTH, expand=True)

        self.aggiorna_combo_diario()
        self.carica_diario()

    def aggiorna_combo_diario(self):
        conn = sqlite3.connect(DB_FILE)
        self.esercizi_dict = {
            f"[{r[2]} | {r[3]}] {r[1]}": r[0] 
            for r in conn.execute("SELECT id, nome, categoria, blocco FROM esercizi ORDER BY categoria, blocco, nome")
        }
        conn.close()
        self.combo_esercizi['values'] = list(self.esercizi_dict.keys())
        if self.combo_esercizi['values']: 
            self.combo_esercizi.current(0)

    def salva_diario(self):
        data_str, ex_key, peso_str, note_str = self.entry_data.get().strip(), self.combo_esercizi.get(), self.entry_peso.get().strip(), self.entry_note_sessione.get().strip()
        if not ex_key or not peso_str:
            messagebox.showerror("Errore", "Seleziona un esercizio e inserisci il peso.")
            return
        try: peso_val = float(peso_str)
        except ValueError:
            messagebox.showerror("Errore", "Il peso deve essere un numero valido.")
            return

        conn = sqlite3.connect(DB_FILE)
        conn.execute("INSERT INTO diario (data, esercizio_id, peso_kg, note_sessione) VALUES (?, ?, ?, ?)", (data_str, self.esercizi_dict[ex_key], peso_val, note_str))
        conn.commit()
        conn.close()
        self.entry_peso.delete(0, END)
        self.entry_note_sessione.delete(0, END)
        self.carica_diario()
        self.aggiorna_grafico()

    def carica_diario(self):
        self.tree_diario.delete(*self.tree_diario.get_children())
        conn = sqlite3.connect(DB_FILE)
        query = """
            SELECT d.id, d.data, '[' || e.categoria || ' | ' || e.blocco || '] ' || e.nome, d.peso_kg, d.note_sessione 
            FROM diario d 
            JOIN esercizi e ON d.esercizio_id = e.id 
            ORDER BY d.data DESC, d.id DESC
        """
        for row in conn.execute(query):
            self.tree_diario.insert("", END, values=row)
        conn.close()

    # --- TAB 3: STATISTICHE ---
    def build_tab_stats(self):
        frame_top = tb.Frame(self.tab_stats, padding=20)
        frame_top.pack(fill=X)

        tb.Label(frame_top, text="Seleziona Esercizio da Analizzare:", font=("Helvetica", 11)).pack(side=LEFT, padx=10)
        self.combo_stats_ex = tb.Combobox(frame_top, state="readonly", bootstyle="primary", width=50)
        self.combo_stats_ex.pack(side=LEFT, padx=5)
        self.combo_stats_ex.bind("<<ComboboxSelected>>", lambda e: self.aggiorna_grafico())

        self.frame_chart = tb.Frame(self.tab_stats, padding=10)
        self.frame_chart.pack(fill=BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(7, 4), dpi=100)
        self.fig.patch.set_facecolor('#222222')
        self.ax.set_facecolor('#222222')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_chart)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)

    def aggiorna_grafico(self):
        self.combo_stats_ex['values'] = list(self.esercizi_dict.keys())
        ex_key = self.combo_stats_ex.get()
        if not ex_key and self.combo_stats_ex['values']:
            self.combo_stats_ex.current(0)
            ex_key = self.combo_stats_ex.get()
        if not ex_key: return

        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT data, peso_kg FROM diario WHERE esercizio_id = ? ORDER BY data ASC", conn, params=(self.esercizi_dict[ex_key],))
        conn.close()

        self.ax.clear()
        if not df.empty:
            self.ax.plot(df['data'], df['peso_kg'], marker='o', color='#00d2ff', linewidth=2.5, markersize=8, label="Carico (kg)")
            self.ax.set_title(f"Progressione: {ex_key}", fontsize=12, fontweight='bold', color='white', pad=15)
            self.ax.set_xlabel("Data", color='white')
            self.ax.set_ylabel("Carico / Zavorra (kg)", color='white')
            self.ax.tick_params(colors='white')
            self.ax.grid(True, linestyle='--', alpha=0.3, color='#aaaaaa')
            self.ax.legend(facecolor='#333333', edgecolor='none', labelcolor='white')
            self.fig.autofmt_xdate()
        else:
            self.ax.text(0.5, 0.5, "Nessun dato registrato per questo esercizio", color="white", ha='center', va='center', transform=self.ax.transAxes, fontsize=12)

        self.fig.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    app = FitnessTrackerApp()
    app.mainloop()
    