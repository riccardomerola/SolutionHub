from CTkToolTip import CTkToolTip
import customtkinter as ctk
import query
import os
import shutil
from logger import log
from datetime import datetime
from expand_text import LargeTextEditor
from CTkMessagebox import CTkMessagebox
from tkinter import filedialog


# Classe per la parte sinistra della finestra principale
class LeftPanel(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Sezione "Tipologia di macchina" / "Settore"
        self.sector_family = ctk.CTkLabel(
            master=self.app.left_frame,
            text="Tipologia di macchina",
            font=("Roboyo", 16, "bold")
        )
        self.sector_family.grid(column=0, row=0, padx=10, pady=10, sticky="nsw")
        self.sector_combobox = ctk.CTkComboBox(
            master=self.app.left_frame,
            values=["Altro", "Fabshop", "Meccanica", "Levigatrici", "Impianti", "Ricambi"],
            state="readonly",
            font=("Roboto", 15),
            dropdown_font=("Roboto", 15)
        )
        self.sector_combobox.grid(column=0, row=1, columnspan=2, padx=10, pady=(0, 10), sticky="ew")
        self.sector_combobox.set("Altro")

        # Sezione "Oggetto"
        self.object_label = ctk.CTkLabel(
            master=self.app.left_frame,
            text="Oggetto",
            font=("Roboto", 16, "bold")
        )
        self.object_label.grid(column=0, row=2, padx=10, pady=10, sticky="nsw")
        self.object_entry = ctk.CTkEntry(
            master=self.app.left_frame,
            placeholder_text="Modello/commessa o oggetto",
            corner_radius=4,
            font=("Roboto", 14)
        )
        self.object_entry.grid(column=0, row=3, columnspan=2, padx=10, pady=(0, 10), sticky="ew")
        self.object_entry.bind("<KeyRelease>", self.insert_upper) # evento per inserire input in maiuscolo

        # Sezione "Descrizione problema"
        self.description_label = ctk.CTkLabel(
            master=self.app.left_frame,
            text="Descrizione del problema",
            font=("Roboto", 16, "bold")
        )
        self.description_label.grid(column=0, row=4, padx=10, pady=10, sticky="nsw")
        self.description_editor_button = ctk.CTkButton(
            master=self.app.left_frame,
            text="📝",
            width=20,
            height=20,
            text_color=self.app.theme["BUTTON_COLOR"],
            fg_color=self.app.theme["BUTTON_FG_COLOR"],
            hover_color=self.app.theme["BUTTON_HOVER_COLOR"],
            command=self.expand_description_editor
        )
        self.description_editor_button.grid(column=1, row=4, padx=10, pady=10, sticky="nse")
        CTkToolTip(
            self.description_editor_button,
            text="Clicca per ingrandire l'area di testo"
        )
        self.description_text = ctk.CTkTextbox(
            master=self.app.left_frame,
            font=("Roboto", 15)
        )
        self.description_text.grid(column=0, row=5, columnspan=2, padx=10, pady=(0, 10), sticky="nsew")

        # Selzione "Soluzioni e note"
        self.solution_label = ctk.CTkLabel(
            master=self.app.left_frame,
            text="Soluzione e note",
            font=("Roboto", 16, "bold")
        )
        self.solution_label.grid(column=0, row=6, padx=10, pady=10, sticky="nsw")
        self.solution_editor_button = ctk.CTkButton(
            master=self.app.left_frame,
            text="📝",
            width=20,
            height=20,
            text_color=self.app.theme["BUTTON_COLOR"],
            fg_color=self.app.theme["BUTTON_FG_COLOR"],
            hover_color=self.app.theme["BUTTON_HOVER_COLOR"],
            command=self.expand_solution_editor
        )
        self.solution_editor_button.grid(column=1, row=6, padx=10, pady=10, sticky="nse")
        CTkToolTip(
            self.description_editor_button,
            text="Clicca per ingrandire l'area di testo"
        )
        self.solution_text = ctk.CTkTextbox(
            master=self.app.left_frame,
            font=("Roboto", 15)
        )
        self.solution_text.grid(column=0, row=7, columnspan=2, padx=10, pady=(0, 10), sticky="nsew")

        # Pulsanti salvataggio e annulla editing, label editing, pulsante chiusura programma
        self.save_button = ctk.CTkButton(
            master=self.app.left_frame,
            text="Salva in database 💾",
            font=("Roboto", 15),
            fg_color="green",
            hover_color="#218838",
            command=self.create_record
        )
        self.save_button.grid(column=0, row=8, columnspan=2, padx=10, pady=10, sticky="ew")
        self.cancel_editing_button = ctk.CTkButton(
            master=self.app.left_frame,
            text="Annulla modifica ⬅️",
            font=("Roboto", 15),
            command=self.cancel_editing
        )
        # Dizionario per tracciamento record in editazione
        self.editing_record = {
            "ID":None,
            "Settore":None,
            "Elemento":None,
            "Problema":None,
            "Soluzione":None,
            "Documentazione":None,
            "Percorso":None,
            "Editazione":0,
            "User":None,
            "Data":None
        }
        self.warning_edit_label = ctk.CTkLabel(
            master=self.app.left_frame,
            text_color="red",
            font=("Roboto", 16, "bold")
        )
        self.exit_button = ctk.CTkButton(
            master=self.app.left_frame,
            text="Esci dal programma ❌",
            font=("Roboto", 15),
            fg_color="red",
            hover_color="#C82333",
            command=self.close_program
        )
        self.exit_button.grid(column=0, row=10, columnspan=2, padx=10, pady=10, sticky="ew")

        # verifica se ci sono record in editazione per warning all'apertura app
        is_editing = query.get_id_editing_record()
        if len(is_editing) > 0:
            self.editing_record['ID'] = is_editing[0]['ID']
            self.show_edit_warning(self.editing_record['ID'])

        # ======================= FINE INIZIALIZZAZIONE DEL FRAME =======================


    # Funzione per pulire i campi di inserimento e la combobox
    def clear_fields(self):
        self.sector_combobox.set("Altro")
        self.object_entry.delete("0", "end")
        self.description_text.delete("0.0", "end")
        self.solution_text.delete("0.0", "end")


    # Funzioni per espandere i textbox di problema e soluzione
    def expand_description_editor(self):
        LargeTextEditor(self, self.description_text)

    def expand_solution_editor(self):
        LargeTextEditor(self, self.solution_text)


    # Funzione per forzare inserimento di Componente in maiuscolo
    def insert_upper(self, event):
        cursor_position = self.object_entry.index("insert")  # recupera la posizione del cursore
        current_text = self.object_entry.get()
        upper_text = current_text.upper()

        if current_text != upper_text:
            self.object_entry.delete(0, "end")
            self.object_entry.insert(0, upper_text)

            self.object_entry.icursor(cursor_position)   # riposiziona il cursore dove si trovava


    # Funzione per verificare i record in editazione nel db
    def show_edit_warning(self, editing_record):
        try:
            self.warning_edit_label.configure(text=f"ATTENZIONE!\nRecord n°[{editing_record}] in modifica da {self.app.user}")
            self.warning_edit_label.grid(column=0, columnspan=2, row=9, padx=10, pady=10, sticky="new")
            self.app.debug_message(f"Aperto record ID [{editing_record}] in modifica")
        except IndexError as indexerror:
            print(f"Nessun record in modifica - IndexError: {indexerror}")
            log("INFO", "Nessun record aperto in modifica all'avvio dell'applicazione")
            self.app.debug_message("Nessun record in modifica all'avvio dell'applicazione")
        except Exception as err:
            print(f"Errore: {err}")
            log("ERROR", f"Error: {err}")
            return


    # Funzione per annullare l'editing in corso
    def cancel_editing(self):
        log("INFO", f"USER={self.app.user} Chiusura modifica del rercod ID [{self.editing_record["ID"]}]")
        query.close_editing(self.editing_record["ID"])    # settaggio a 0 del valore di editazione

        # rimozione del label di avviso e del pulsante "Annulla"
        self.warning_edit_label.grid_remove()
        self.cancel_editing_button.grid_remove()
        self.save_button.grid(columnspan=2)

        self.editing_record = {
            "ID":None,
            "Settore":None,
            "Elemento":None,
            "Problema":None,
            "Soluzione":None,
            "Documentazione":None,
            "Percorso":None,
            "Editazione":0,
            "User":None,
            "Data":None
        }
        self.clear_fields()             # pulizia dei campi di inserimento


    # Funzione per inserire il record nel database
    def insert_record(self, document="", root=None):
        self.app.update_idletasks()

        sector = self.sector_combobox.get()
        object = self.object_entry.get().strip()
        description = self.description_text.get("1.0", "end-1c").strip()
        solution = self.solution_text.get("1.0", "end-1c").strip()
        edit = 0
        self.user = os.getlogin()
        date = datetime.now().strftime("%d-%m-%Y")

        if self.editing_record['ID'] is not None:
            self.new_id = self.editing_record['ID']
            query.edit_record(self.new_id, sector, object, description, solution, document, root, edit, self.user, date)
            self.app.right_panel.load_data()
            self.cancel_editing()
            return
        else:
            query.insert_record(self.new_id, sector, object, description, solution, document, root, edit, self.user, date)
            self.app.right_panel.load_data()
            self.clear_fields()
            return


    # Funzione creare il record da inserire nel database
    def create_record(self):
        if self.object_entry.get().strip() == "" or self.description_text.get("1.0", "end-1c").strip() == "" or self.solution_text.get("1.0", "end-1c").strip() == "":
            CTkMessagebox(
                title="Campi vuoti",
                message='Prima di salvare è necessario riempire i campi "Oggetto", "Descrizione", "Soluzione"',
                icon="warning",
                border_width=2,
                border_color="orange",
                option_1="Ok"
            )
            return

        # se il record da aggiungere è aperto in modifica
        if self.editing_record['ID'] is not None:
            document = self.editing_record['Documentazione']
            root = self.editing_record['Percorso']
            self.insert_record(document, root)
            return

        raw_row = query.get_max_id()
        self.max_id = raw_row[0]['ID'] if raw_row else 0
        self.new_id = self.max_id + 1

        msg = CTkMessagebox(
            title="Allega file",
            message="Vuoi allegare un file al record?",
            icon="info",
            border_width=2,
            border_color="#0061FF",
            option_1="Si",
            option_2="No",
            justify="center"
        )

        # richiesta inserimento allegato
        if msg.get() == "No":
            document = "No"
            root = None

            self.insert_record(document, root)

            log("INFO", f"USER={self.user} Aggiunto nuovo record ID [{self.new_id}] senza file allegato")
            self.app.debug_message(f'Aggiunto nuovo record ID [{self.new_id}] senza file allegato')
            return
        else:
            selected_file = filedialog.askopenfilename(
                title="Seleziona un file",
                filetypes=[("Tutti i file", "*.*")]
            )
            if not selected_file:
                self.insert_record(document="No", root=None)
                log("WARNING", f"USER={self.user} Nessun file allegao al record ID [{self.new_id}] appena inserito")
                self.app.debug_message(f"Attenzione: nessun file allegato al record ID [{self.new_id}] appena inserito")
                return
            else:
                original_filename = os.path.basename(selected_file) # estrae l'ultimo componente di un percorso (qui è il nome file)
                new_filename = f"{self.new_id}_{original_filename}" # modifica del nome con aggiunta ID all'inizio
                root = os.path.join(self.app.documents_root, new_filename) # percorso completo ottenuto unendo root e nuovo nome file

                # verifica esistenza del percorso (True o False)
                if not os.path.isfile(root):
                    self.insert_record(document="Si", root=root)
                    shutil.copy(selected_file, root)    # copia il file al percorso
                    log("INFO", f'USER={self.user} Aggiunto nuovo record ID [{self.new_id}] con documento "{new_filename}" allegato')
                    self.app.debug_message(f'Aggiunto nuovo record ID [{self.new_id}] con documento "{new_filename}" allegato')


    # Funzione per la chiusura del programma
    def close_program(self):

        self.app.destroy()

        if self.editing_record is not None:
            msg = CTkMessagebox(
                title="Record in modifica!",
                message=f"Prima di chiudere l'app è necessario terminare la modifica del record ID [{self.editing_record}]",
                icon="warning",
                border_width=2,
                border_color="orange",
                option_1="Esci senza salvare",
                option_2="Salva ed esci",
                justify="center"
            )

            log("WARNING", f"USER={self.app.user} Terminare la modifica prima di chiudere l'applicazione")
            self.app.debug_message("Terminare la modifica del record in corso prima di chiudere l'applicazione")

            if msg.get() == "Salva ed esci":
                log("INFO", f"USER={self.app.user} Modifica salvata e chiusura dell'applicazione")
                self.insert_record()
                self.destroy()
            elif msg.get() == "Esci senza salvare":
                query.close_editing(self.editing_record)
                log("INFO", f"USER={self.app.user} Modifica annullata e chiusura dell'applicazione")
                self.app.destroy()
            return
        else:
            log("INFO", f"USER={self.app.user} Chiusura dell'applicazione")
            self.app.destroy()