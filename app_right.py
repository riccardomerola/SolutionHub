from CTkToolTip import CTkToolTip
import customtkinter as ctk
from tkinter import ttk
import query
from detail_window import DetailWindow

# Classe per la parte destra della finestra principale
class RightPanel(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master)
        self.app = app
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Barra di ricerca e combobox filtri
        self.search_entry = ctk.CTkEntry(
            master=self.app.right_frame,
            placeholder_text="🔎 Cerca",
            height=40,
            corner_radius=4,
            font=("Roboto", 18)
        )
        self.search_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.dynamic_search)

        self.filter_combobox = ctk.CTkComboBox(
            master=self.app.right_frame,
            height=40,
            width=300,
            values=["Nessun filtro di ricerca", "Altro", "Fabshop", "Meccanica", "Levigatrici", "Impianti", "Ricambi"],
            state="readonly",
            font=("Roboto", 18),
            dropdown_font=("Roboto", 15),
            command=self.load_data
        )
        self.filter_combobox.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="e")
        self.filter_combobox.set("Nessun filtro di ricerca")

        # Eventi per evidenziare la combobox
        self.search_entry.bind("<Enter>", self.on_hover)
        self.search_entry.bind("<Leave>", self.on_leave)

        # =================== TABELLA TREEVIEV ===================
        self.table_frame = ctk.CTkFrame(master=self.app.right_frame, corner_radius=4)
        self.table_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.table_frame.grid_columnconfigure((0, 1), weight=1)
        self.table_frame.grid_rowconfigure((0, 1), weight=1)

        # Stile ttk, scrollbar
        self.style = ttk.Style()
        self.style.theme_use("winnative")
        self.scrollbar_y = ctk.CTkScrollbar(master=self.table_frame, orientation="vertical")

        # Stile della heading e delle celle della tabella
        self.style.configure(
            "Treeview.Heading",
            background=self.app.theme["BG_COLOR_HEADING"],
            foreground=self.app.theme["FG_COLOR"],
            borderwidth=1,
            relief="solid",
            padding=(0, 8, 0, 8),
            font=("Roboto", 15, "bold")
        )
        self.style.configure(
            "Treeview",
            background=self.app.theme["BG_COLOR_TREEVIEW"],
            foreground=self.app.theme["FG_COLOR"],
            fieldbackground=self.app.theme["BG_COLOR_TREEVIEW"],
            rowheight=40,
            borderwidth=1,
            relief="flat",
            font=("Roboto", 11)
        )
        self.style.map("Treeview", background=[("selected", "#3b8ed0")])

        # Creazione della tabella
        self.value_table = ttk.Treeview(
            master=self.table_frame,
            columns=("id", "sector", "object", "problem", "solution", "doc"),
            show="headings",
            yscrollcommand=self.scrollbar_y.set
        )
        CTkToolTip(
            self.value_table,
            message="Doppio click sul record per aprire il dettaglio",
            corner_radius=8,
            border_width=1,
            border_color="white"
        )
        # Heading delle colonne
        self.value_table.heading("id", text="ID")
        self.value_table.heading("sector", text="Settore")
        self.value_table.heading("object", text="Oggetto")
        self.value_table.heading("problem", text="Problema")
        self.value_table.heading("solution", text="Soluzione")
        self.value_table.heading("doc", text="Allegato")

        # Impostazione delle colonne
        self.value_table.column("id", width=15, stretch=True, anchor="center")
        self.value_table.column("sector", width=90, stretch=True, anchor="center")
        self.value_table.column("object", width=100, stretch=True, anchor="center")
        self.value_table.column("problem", width=400, stretch=True, anchor="w")
        self.value_table.column("solution", width=400, stretch=True, anchor="w")
        self.value_table.column("doc", width=80, stretch=True, anchor="center")

        # Definizione dei tag per le righe della tabelle
        self.value_table.tag_configure("pari", background=self.app.theme["BG_COLOR_TREEVIEW"])
        self.value_table.tag_configure("dispari", background=self.app.theme["BG_COLOR_TREEVIEW_ALTERNATE"])
        self.value_table.tag_configure("nessun_risultato", foreground="orange")

        # Posizionamento della tabella e della scrollbar
        self.scrollbar_y.configure(command=self.value_table.yview)
        self.scrollbar_y.pack(side="right", fill="y")
        self.value_table.pack(padx=0, pady=0, fill="both", expand=True)

        # Eventi per la gestione dei click sulla tabella
        self.value_table.bind("<<TreeviewSelect>>", self.handle_table_click)
        self.value_table.bind("<Double-1>", self.handle_double_click)

        # Pulsante per visualizzare il dettaglio del record selezionato
        self.open_detail = ctk.CTkButton(
            master=self.app.right_frame,
            text="Apri dettaglio del record selezionato ℹ️",
            font=("Roboto", 15),
            command=self.handle_double_click
        )
        self.open_detail.grid(column=0, row=2, columnspan=2, padx=10, pady=10, sticky="ew")

        # ======================= FINE INIZIALIZZAZIONE DEL FRAME =======================


    # Funzione per evidenziare la combobox del filtro al passaggio del mouse
    def on_hover(self, event):
        self.filter_combobox.configure(
            border_color=("#1f6aa5", "#144870"),
            fg_color=("#ebebeb", "#2a2d2e"),
            button_hover_color=("#1f6aa5", "#1f6aa5"),
            button_color=("#1f6aa5", "#1f6aa5"),
            border_width=4
        )

    def on_leave(self, event):
        self.filter_combobox.configure(
            border_color=("#979da2", "#565b5e"),
            fg_color=("#f9f9fa", "#343638"),
            button_hover_color=("#1f6aa5", "#1f6aa5"),
            button_color=("#979da2", "#565b5e"),
            border_width=1
        )


    # Funzione per recuperare l'elemento selezionato
    def get_selected_row(self):
        selected = self.value_table.selection() # recupera l'elemento

        if not selected:
            return

        # si prende il primo elemento, si estrapolano i valori in lista e si seleziona id
        item = selected[0]
        values = self.value_table.item(item)["values"]
        record_id = values[0]
        return record_id


    # Funzione per gestire la selezione di una riga nella tabella
    def handle_table_click(self, event=None):
        record_id = self.get_selected_row()

        # cerca il record e lo salva in self.selected_row_data
        for row in self.formatted_data:
            if row[0] == record_id:
                self.selected_row_data = row
                break


    # Funzione per gestire il doppio click su una riga della tabella
    def handle_double_click(self, event=None):
        record_id = self.get_selected_row()

        # cerca il record e apre la finestra DetailWindow passnado le sue info
        for row in self.formatted_data:
            if row[0] == record_id:
                DetailWindow(self, row)
                break


    # Funzione per formattare i dati del db in liste di liste per la Treeview
    def format_data(self, rows):
        formatted_data = []

        for row in rows:
            formatted_data.append(
                [row['ID'],
                 row['Settore'],
                 row['Oggetto'],
                 row['Problema'],
                 row['Soluzione'],
                 row['Documentazione'],
                 row['Percorso'],
                 row['Editazione'],
                 row['User'],
                 row['Data']]
            )
        return formatted_data


    # Funzione per caricare i dati del db dentro alla Treeview
    def load_data(self, *args, **kwargs):
        # pulizia della tabella prima dell'inserimento dei nuovi dati (evita duplicati)
        for item in self.value_table.get_children():
            self.value_table.delete(item)

        # Si leggono i valori della barra di ricerca e del filtro per capire quali dati caricare nella tabella
        current_filter = self.filter_combobox.get()
        active_filter = current_filter != "Nessun filtro di ricerca"

        raw_text = self.search_entry.get()
        clean_text = raw_text.strip() if raw_text else ""
        clean_text_exist = clean_text != ""

        # Selezione della query di ricerca in base al testo scritto e al filtro inserito
        if clean_text_exist and active_filter:
            raw_rows = query.search_with_filter(clean_text, current_filter)
        elif clean_text_exist:
            raw_rows = query.search(clean_text)
        elif active_filter:
            raw_rows = query.search_only_filter(current_filter)
        else:
            raw_rows = query.get_database()

        self.formatted_data = self.format_data(raw_rows)

        if not self.formatted_data:
            self.value_table.column("problem", width=400, stretch=True, anchor="center")
            self.value_table.column("solution", width=400, stretch=True, anchor="center")
            empty_message = ["⚠️", "⚠️", "⚠️", "Nessun risultato trovato", "⚠️", "⚠️", "⚠️", "⚠️", "⚠️", "⚠️"]
            self.value_table.insert("", "end", values=empty_message, tags=("nessun_risultato", ))
        else:
            for i, row in enumerate(self.formatted_data):
                tag_row = "pari" if i % 2 == 0 else "dispari"
                # visualzza una riga per colonna e rende ordine nella visualizzazione
                viewed_columns = list(row[:6])
                viewed_columns[2] = f"       {str(viewed_columns[2]).split('\n')[0]}     "
                viewed_columns[3] = f"       {str(viewed_columns[3]).split('\n')[0]}     "
                viewed_columns[4] = f"       {str(viewed_columns[4]).split('\n')[0]}     "
                self.value_table.insert("", "end", values=viewed_columns, tags=(tag_row, ))

        self.selected_row_data = None
        self.app.debug_message(f"Record trovati: {len(raw_rows)}")


    # Funzione per la ricerca dinamica (senza clic di Enter per l'avvio)
    def dynamic_search(self, event=None):
        # reset timer precedente se l'utente clicca un pulsante prima di 400ms
        if hasattr(self, 'search_timer') and self.search_timer is not None:
            self.after_cancel(self.search_timer)
            self.search_timer = None

        # event si attiva al rilascio di un tasto dalla tastiera
        if event is not None:
            # pianifica di richiamare la funzione forzando event=None impostando tempo scaduto
            self.search_timer = self.after(300, lambda: self.dynamic_search(event=None))

        self.after_idle(self.load_data)     # aggiorna la tabella alla fine dei processi
        self.search_timer = None            # reset del timer pronto alla prossima ricerca
