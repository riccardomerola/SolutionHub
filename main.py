# Istruzioni per la gestione della scala di windows degli utenti
import sys
if sys.platform.startswith("win"):
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

# Importazione librerie e moduli necessari
from tkinter import filedialog, ttk
from CTkMessagebox import CTkMessagebox
from CTkMenuBar import CTkMenuBar, CustomDropdownMenu
from CTkToolTip import CTkToolTip
import customtkinter as ctk
import shutil
from logger import log
import db
import query
import os
from datetime import datetime
from detail_window import DetailWindow
from drop_menu import MenuBar
from expand_text import LargeTextEditor
from app_left import LeftFrame
from theme import THEMES

ctk.set_appearance_mode("System")   # imposta il tema del sistema
ctk.set_default_color_theme("blue") # imposta i colori sul blu
mode = ctk.get_appearance_mode()
documents_root = r"Documents"

ctk.deactivate_automatic_dpi_awareness()    # disattiva gestione automatica della scala di windows

# Classe della finestra principale
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Breton Solution Hub")
        self.center_win_app(1600, 950)
        self.resizable(True, True)
        self.user = os.getlogin()
        log("INFO", f"USER={self.user} Apertura dell'applicazione")

        # Selezione del tema in base al tema del sistema operativo
        self.theme_name = ctk.get_appearance_mode()
        self.theme = THEMES[self.theme_name]

        # Controllo chiusura del programma tramite "X" della finestra



        # configurazione griglia principale
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ======================= MENU APPLICAZIONE =======================
        menu_bar = CTkMenuBar(master=self)
        self.action_menu = MenuBar(master=self)

        file_button = menu_bar.add_cascade("File")
        help_button = menu_bar.add_cascade("Help")
        info_button = menu_bar.add_cascade("Info")

        file_dropdown = CustomDropdownMenu(widget=file_button)
        #file_dropdown.add_option(option="Cambia database", command=self.action_menu.change_database)
        #file_dropdown.add_separator()
        file_dropdown.add_option(option="Cambia tema", command=self.action_menu.view_theme_option)
        file_dropdown.add_separator()
        #file_dropdown.add_option(option="Esci", command=self.left_frame.close_program)

        # Creazione schermata di debug senza posizionarla
        self.frame_textbox = ctk.CTkFrame(self)
        self.textbox_debug = ctk.CTkTextbox(
            self.frame_textbox,height=300,
            width=500,
            state="disabled"
        )
        self.button_close_debug = ctk.CTkButton(
            self.frame_textbox,
            text="Chiudi debug",
            command=self.action_menu.close_debug
        )
        self.button_close_debug.pack(pady=10, side="left")
        self.textbox_debug.pack(pady=10, padx=10, fill="both", expand=True)

        # Creazione menu a tendina per le voci Help e Info
        help_button = CustomDropdownMenu(widget=help_button)
        help_button.add_option(option="Debug", command=self.action_menu.open_debug)
        help_button.add_option(option="Istruzioni per l'utilizzo", command=self.action_menu.open_instruction)
        help_button.add_option(option="Reset stato di modifica", command=self.action_menu.reset_edit)

        info_button = CustomDropdownMenu(widget=info_button)
        info_button.add_option(option="Versione software", command=self.action_menu.open_info)
        info_button.add_option(option="Segnala problemi o bug", command=self.action_menu.signal_problem)

        # ======================= FRAME CONTENENTE TUTTA LA PAGINA ========
        # Necessario perché CTkMenuBar usa .pack() e non .grid(): i due non possono coesistere nello stesso frame
        self.frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frame.pack(fill="both", expand=True)

        # configurazione griglia principale
        self.frame.grid_columnconfigure(0, weight=0)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        # ======================= FRAME DI SINISTRA =====================
        self.left_frame = LeftFrame(self)
        self.protocol("WM_DELETE_WINDOW", self.left_frame.close_program)

        # ======================= FRAME DI DESTRA =======================
        self.right_frame = ctk.CTkFrame(self.frame, corner_radius=4)
        self.right_frame.grid(row=0, padx=10, pady=10, column=1, sticky="nsew")
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # Entry della barra di ricerca
        self.search_entry = ctk.CTkEntry(
            self.right_frame,
            placeholder_text="🔎 Cerca",
            height=40,
            corner_radius=4,
            font=("Roboto", 18)
        )
        self.search_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.dynamic_search)     # evento per la ricerca dinamica al rilascio del tasto

        # Combobox per i filtri della ricerca
        self.filter_combobox = ctk.CTkComboBox(
            self.right_frame,
            height=40,
            width=300,
            values=["Nessun filtro di ricerca", "Altro", "Fabshop", "Meccanica", "Levigatrici", "Impianti", "Ricambi"],
            state="readonly",
            font=("Roboto", 18),
            dropdown_font=("Roboto", 15),
            command=self.load_data
        )
        self.filter_combobox.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="e")
        self.filter_combobox.set("Nessun filtro di ricerca")    # valore di default della combobox

        # Eventi per evidenziare la combobox al passaggio del mouse sulla barra di ricerca
        self.search_entry.bind("<Enter>", self.on_hover)
        self.search_entry.bind("<Leave>", self.on_leave)

        # =========== Frame, stile, gestione click della Tabella ttk.TreeView ===========
        # Frame in cui inserire la tabella
        self.table_frame = ctk.CTkFrame(self.right_frame, corner_radius=4)
        self.table_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.table_frame.grid_columnconfigure((0, 1), weight=1)
        self.table_frame.grid_rowconfigure((0, 1), weight=1)

        # CREAZIONE TABELLA TreeView E Stile ttk
        self.style = ttk.Style()
        self.style.theme_use("winnative")

        # creazione della scrollbar_y per la tabella TreeView
        self.scrollbar_y = ctk.CTkScrollbar(self.table_frame, orientation="vertical")

        # configurazione stile della heading e delle celle della tabella
        self.style.configure(
            "Treeview.Heading",
            background=self.theme["BG_COLOR_HEADING"],
            foreground=self.theme["FG_COLOR"],
            borderwidth=1,
            relief="solid",
            padding=(0, 8, 0, 8),
            font=("Roboto", 15, "bold")
        )
        self.style.configure(
            "Treeview",
            background=self.theme["BG_COLOR_TREEVIEW"],
            foreground=self.theme["FG_COLOR"],
            rowheight=40,
            fieldbackground=self.theme["BG_COLOR_TREEVIEW"],
            borderwidth=1,
            relief="flat",
            font=("Roboto", 11)
        )
        self.style.map("Treeview", background=[("selected", "#3b8ed0")])
        # creazione tabella
        self.value_table = ttk.Treeview(
            self.table_frame,
            columns=("id", "sector", "object", "problem", "solution", "doc"),
            show="headings",
            yscrollcommand=self.scrollbar_y.set
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
        self.value_table.tag_configure("pari", background=self.theme["BG_COLOR_TREEVIEW"])
        self.value_table.tag_configure("dispari", background=self.theme["BG_COLOR_TREEVIEW_ALTERNATE"])
        self.value_table.tag_configure("nessun_risultato", foreground="orange")

        # Posizionamento della tabella e della scrollbar
        self.scrollbar_y.configure(command=self.value_table.yview)
        self.scrollbar_y.pack(side="right", fill="y")
        self.value_table.pack(padx=0, pady=0, fill="both", expand=True)

        # Tooltip per indicare che con doppio click si apre il dettaglio
        CTkToolTip(
            self.value_table,
            message="Doppio click sul record per aprire il dettaglio",
            corner_radius=8,
            border_width=1,
            border_color="white"
        )

        self.load_data()

        # Eventi per la gestione dei click sulla tabella
        self.value_table.bind("<<TreeviewSelect>>", self.handle_table_click)
        self.value_table.bind("<Double-1>", self.handle_double_click)

        # Azzeramento attributi
        self.selected_row_data = None       # dati della riga selezionata nella tabella
        self.record_edit_id = None          # id del record in editazione
        self.editing_actual_record = None   # flag per indicare se si sta modificando un record o meno
        self.record_edit_document = None    # nome del documento del record in editazione
        self.record_edit_root = None        # percorso del documento del record in editazione

        # Pulsante per visualizzare il dettaglio del record selezionato
        self.open_detail = ctk.CTkButton(
            master=self.right_frame,
            text="Apri dettaglio del record selezionato ℹ️",
            font=("Roboto", 15),
            command=self.handle_double_click
        )
        self.open_detail.grid(column=0, row=2, columnspan=2, padx=10, pady=10, sticky="ew")

        #self.show_edit_warning(self.record_edit_id) # verifica se ci sono record in editazione
        self.update()                               # aggiorna la finestra per visualizzare il messaggio record in editazione

        # Funzione per chiudere la finestra di splash screen se presente
        try:
            import pyi_splash   # type: ignore
            pyi_splash.close()
        except ImportError:
            pass

        # ====================== FINE INIZIALIZZAZIONE DELLA FINESTRA PRINCIPALE ======================


    # Funzione per evidenziare la combobox del filtro quando si passa sopra la barra di ricerca
    def on_hover(self, event):
        self.filter_combobox.configure(
            border_color=("#1f6aa5", "#144870"),
            fg_color=("#ebebeb", "#2a2d2e"),
            button_hover_color=("#1f6aa5", "#1f6aa5"),
            button_color=("#1f6aa5", "#1f6aa5"),
            border_width=4
        )

    # Funzione per ripristinare i colore della combobox del filtro quando si toglie il mouse dalla barra di ricerca
    def on_leave(self, event):
        self.filter_combobox.configure(
            border_color=("#979da2", "#565b5e"),
            fg_color=("#f9f9fa", "#343638"),
            button_hover_color=("#1f6aa5", "#1f6aa5"),
            button_color=("#979da2", "#565b5e"),
            border_width=1
        )


    # Funzione per applicare il tema selezionato al programma
    def apply_theme(self):
        # Applicazione temi della tabella
        self.style.configure(
            "Treeview.Heading",
            background=self.theme["BG_COLOR_HEADING"],
            foreground=self.theme["FG_COLOR"]
        )
        self.style.configure(
            "Treeview",
            background=self.theme["BG_COLOR_TREEVIEW"],
            foreground=self.theme["FG_COLOR"],
            fieldbackground=self.theme["BG_COLOR_TREEVIEW"]
        )
        self.value_table.tag_configure("pari", background=self.theme["BG_COLOR_TREEVIEW"])
        self.value_table.tag_configure("dispari", background=self.theme["BG_COLOR_TREEVIEW_ALTERNATE"])

        # Applicazione temi dei pulsanti
        self.button_expand_description.configure(
            text_color=self.theme["BUTTON_COLOR"],
            fg_color=self.theme["BUTTON_FG_COLOR"],
            hover_color=self.theme["BUTTON_HOVER_COLOR"]
        )
        self.button_expand_problem.configure(
            text_color=self.theme["BUTTON_COLOR"],
            fg_color=self.theme["BUTTON_FG_COLOR"],
            hover_color=self.theme["BUTTON_HOVER_COLOR"]
        )


    # Funzione per centrare la finestra nello schermo
    def center_win_app(self, width, height):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight() - 80
        scale = self._get_window_scaling()

        x = int(((screen_width / 2) - (width / 2)) * scale)
        y = int(((screen_height / 2) - (height / 2)) * scale)
        self.geometry(f"{width}x{height}+{x}+{y}")


    # Funzione per recuperare l'elemento selezionato
    def get_selected_row(self):
        selected = self.value_table.selection()     # recupera l'elemento selezionato

        if not selected:
            return None

        # si prende il primo elemento selezionato, si estrapolano i valori in una lista e si seleziona l'id
        item = selected[0]
        values = self.value_table.item(item)["values"]
        record_id = values[0]
        return record_id


    # Funzione per gestire la selezione di una riga nella tabella
    def handle_table_click(self, event=None):
        record_id = self.get_selected_row()

        # cerca nella lista completa il record con quell'id e lo salva in self.selected_row_data
        for row in self.formatted_data:
            if row[0] == record_id:
                self.selected_row_data = row
                break


    # Funzione per l'apertura della finestra al doppio click
    def handle_double_click(self, event=None):
        record_id = self.get_selected_row()

        # cerca nella lista completa il record con quell'id e apre la finestra DetailWindow passando le informazioni
        for row in self.formatted_data:
            if row[0] == record_id:
                DetailWindow(self, row)
                break


    # Funzione per formattare i dati del database in liste di liste per la CTkTable
    def format_data(self, rows):
        formatted_data = []

        for row in rows:
            formatted_data.append(
                [row['ID'],
                 row['Settore'],
                 row['Elemento'],
                 row['Problema'],
                 row['Soluzione'],
                 row['Documentazione'],
                 row['Percorso'],
                 row['Editazione'],
                 row['User'],
                 row['Data']]
            )
        return formatted_data


    # Funzione per caricare i dati del database dentro alla tabella
    def load_data(self, *args, **kwargs):
        # pulizia della tabella per inserimento dei dati aggiornati (per evitare duplicati)
        for item in self.value_table.get_children():
            self.value_table.delete(item)

        current_filter = self.filter_combobox.get()
        active_filter = current_filter != "Nessun filtro di ricerca"    # True o False

        raw_text = self.search_entry.get()
        clean_text = raw_text.strip() if raw_text else ""
        clean_text_exist = clean_text != ""     # True o False

        # Selezione della query di ricerca da chiamare in base alla presenza del filtro
        if clean_text_exist and active_filter:
            raw_rows = query.search_with_filter(clean_text, current_filter)
        elif clean_text_exist:
            raw_rows = query.search(clean_text)
        elif active_filter:
            raw_rows = query.search_only_filter(current_filter)
        else:
            raw_rows = query.get_database()     # lista di dizionari (coppie key-value)

        self.formatted_data = self.format_data(raw_rows)

        # Popolazione della tabella (diversa se sono stati trovati record o meno dalla ricerca)
        if not self.formatted_data:
            self.value_table.column("problem", width=400, stretch=True, anchor="center")
            self.value_table.column("solution", width=400, stretch=True, anchor="center")
            empty_message = ["⚠️", "⚠️", "⚠️", "Nessun risultato trovato", "⚠️", "⚠️", "⚠️", "⚠️", "⚠️", "⚠️"]
            self.value_table.insert("", "end", values=empty_message, tags=("nessun_risultato", ))
        else:
            for i, row in enumerate(self.formatted_data):
                tag_row = "pari" if i % 2 == 0 else "dispari"
                # modifica per visualizzare una sola riga per ogni colonna (rende ordine nella visualizzazione della tabella)
                viewed_columns = list(row[:6])
                viewed_columns[2] = f"       {str(viewed_columns[2]).split('\n')[0]}     "
                viewed_columns[3] = f"       {str(viewed_columns[3]).split('\n')[0]}     "
                viewed_columns[4] = f"       {str(viewed_columns[4]).split('\n')[0]}     "
                self.value_table.insert("", "end", values=viewed_columns, tags=(tag_row, ))

        self.selected_row_data = None
        self.debug_message(f"Record trovati: {len(raw_rows)}")


    # Funzione per leggere il contenuto dei Textbox (frame di sinistra)
    def insert_record(self):
        self.update_idletasks()
        raw_row = query.get_max_id()
        current_id = raw_row[0]["ID"] if raw_row else 0

        sector = self.combobox_family.get()
        element = self.entry_component.get().strip()
        description = self.text_description.get("1.0", "end-1c").strip()
        document = ""
        solution = self.text_solution.get("1.0", "end-1c").strip()
        root = None
        self.user = os.getlogin()
        data = datetime.now().strftime("%d-%m-%Y")
        edit = 0

        # controllo se i campi non sono vuoti
        if element.strip() == "" or description.strip() == "" or solution.strip() == "":
            msg_empty = CTkMessagebox(
                title="Campi vuoti",
                message='Prima di salvare è necessario riempire i campi "Oggetto", "Descrizione" e "Soluzione"',
                icon="warning",
                border_width=2,
                border_color="orange",
                option_1="Ok"
            )
            return

        if self.record_edit_id is not None:
            record_id = self.record_edit_id
            document = self.record_edit_document
            root = self.record_edit_root
            self.user = os.getlogin()
            data = datetime.now().strftime("%d-%m-%Y")
            edit = 0

            query.edit_record(record_id, sector, element, description, solution, document, root, edit, self.user, data)
            log("INFO", f"USER={self.user} Salvata modifica su record ID [{record_id}]")
            self.debug_message(f'Salvata modifica su record ID [{record_id}]')
            self.record_edit_id = None
            self.editing_actual_record = None
            self.editing_id = None
            self.load_data()

            self.label_warning_edit.grid_remove()
            self.button_cancel_editing.grid_remove()
            self.button_save.grid(columnspan=2)
            self.clear_fields()
            self.label_warning_edit.destroy()
            self.label_warning_edit = None
        else:
            # Calcola ID del nuovo record e legge le entry
            record_id = int(current_id) + 1

            # Messaggio per chiedere se si vuole allegare un file
            msg = CTkMessagebox(
                title="Allega file",
                message="Vuoi allegare un file al record?",
                icon="info",
                border_width=2,
                border_color="#0061ff",
                option_1="Si",
                option_2="No",
                justify="center"
            )

            # Se non si vuole aggiungere un file
            if msg.get() == "No":
                document = "No"

                query.insert_record(record_id, sector, element, description, solution, document, root, edit, self.user, data)
                self.load_data()
                log("INFO", f"USER={self.user} Aggiunto nuovo record ID [{record_id}] senza file allegato")
                self.debug_message(f'Aggiunto nuovo record ID [{record_id}] senza file allegato')

                self.clear_fields()
                return

            # Apre file explorer: restituisce il percorso in stringa se seleziona file, altrimenti stringa vuota
            selected_file = filedialog.askopenfilename(title="Seleziona un file",
                                                       filetypes=[("Tutti i file", "*.*")])

            # Se si clicca "Si" ma non si seleziona nessun file
            if not selected_file:
                document = "No"

                query.insert_record(record_id, sector, element, description, solution, document, root, edit, self.user, data)
                self.load_data()
                log("WARNING", f"USER={self.user} Nessun file allegato al record ID [{record_id}] appena inserito")
                self.debug_message(f'Attenzione: nessun file allegato al record ID [{record_id}] appena inserito')
                self.clear_fields()
                return

            file = os.path.basename(selected_file)                          # estrae l'ultimo componente da un percorso (qui è nome file)
            filename = f"{record_id}_{file}"                                # modifica il nome del file aggiungendo ID all'inizio
            destination_path = os.path.join(documents_root, filename)       # combina segmenti creando il percorso con separatori

            # Verifica se il percorso esiste, restituisce True o False
            if not os.path.isfile(destination_path):
                shutil.copy(selected_file, destination_path)  # copia file al percorso
                document = "Si"
                root = destination_path

                query.insert_record(record_id, sector, element, description, solution, document, root, edit, self.user, data)
                log("INFO", f'USER={self.user} Aggiunto nuovo record ID [{record_id}] con documento "{filename}" allegato')
                self.debug_message(f'Aggiunto nuovo record ID [{record_id}] con documento "{filename}" allegato')
                self.load_data()
                self.clear_fields()
                self.update()
                return

            # Messaggio che avvisa di file con stesso nome già presente
            msg_exist = CTkMessagebox(
                title="File esistente",
                message=f'Esiste già un file "{filename}" relativo al record ID[{record_id}].\nVuoi sovrascriverlo?',
                icon="warning",
                border_width=2,
                border_color="orange",
                option_1="Si",
                option_2="No",
                justify="center"
            )

            if msg_exist.get() == "No":
                document = "No"

                query.insert_record(record_id, sector, element, description, solution, document, root, edit, self.user, data)
                log("INFO", f'USER={self.user} Aggiunto record [{record_id}] senza documento allegato (documento "{filename}" già esistente)')
                self.debug_message(f'Aggiunto record [{record_id}] senza documento allegato (documento già esistente)')
                self.load_data()
                self.clear_fields()
                return

            # Se si vuole sovrascrivere
            shutil.copy(selected_file, destination_path)    # copia file al percorso
            document = "Si"
            root = destination_path

            query.insert_record(record_id, sector, element, description, solution, document, root, edit, self.user, data)
            log("INFO", f'USER={self.user} Aggiunto record ID [{record_id}] con documento allegato (documento "{filename}" sovrasctitto)')
            self.debug_message(f'Aggiunto record ID [{record_id}] con documento allegato (documento "{filename}" sovrasctitto)')
            self.load_data()

            self.clear_fields()

    # Funzione per ricerca dinamica
    def dynamic_search(self, event=None):
        # reset timer precedente se l'utente clicca un pulsante prima di 400ms
        if hasattr(self, 'search_timer') and self.search_timer is not None:
            self.after_cancel(self.search_timer)
            self.search_timer = None

        # event si attiva al rilascio di un tasto sulla tastiera
        if event is not None:
            # pianifica di richiamare la funzione forzando event=None per impostare tempo scaduto
            self.search_timer = self.after(300, lambda: self.dynamic_search(event=None))
            return

        self.after_idle(self.load_data) # aggiorna la tabella quando sono finiti altri processi
        self.search_timer = None        # reset del timer pronto per la prossima ricerca


    # Funzione per inserire messaggi nella textbox di debug
    def debug_message(self, message):
        self.textbox_debug.configure(state="normal")
        self.textbox_debug.insert("end", f"-> {message}\n")
        self.textbox_debug.see("end")
        self.textbox_debug.configure(state="disabled")



# ======================== AVVIAMENTO DEL PROGRAMMA ========================
if __name__ == "__main__":
    db_integrity = query.check_db_integrity()

    if db_integrity == "ok":
        log("INFO", "Integrità database: OK")
        db_path = r"Database\breton_solutionhub.db"
        # creazione cartella di backup
        bck_folder = r"Database\backup"
        if not os.path.exists(bck_folder):
            os.makedirs(bck_folder)

        # creazione file di backup
        bck_name = f"backup_{datetime.now().strftime('%Y_%m_%d')}.db"
        bck_path = os.path.join(bck_folder, bck_name)

        if not os.path.exists(bck_path):
            try:
                shutil.copy2(db_path, bck_path)
                log("INFO", f"Creato backup del database '{bck_name}'")
            except Exception as err:
                log("ERROR", str(err))

        db.create_table()
        app = App()
        app.mainloop()
    else:
        log("CRITICAL", f"Errore di integrità del database - ERR: {db_integrity}")
        pass

    pass