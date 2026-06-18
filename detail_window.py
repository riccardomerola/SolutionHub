import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from logger import log
import query
import os
from replace_doc_window import DocumentExistAllert
from new_doc_window import DocumentNotExistAllert
from cancel_window import CancelConfirm

mode = ctk.get_appearance_mode()

# Classe della finestra di dettaglio
class DetailWindow(ctk.CTkToplevel):
    def __init__(self, master, data):
        super().__init__(master)
        self.selected_row_data = self.master.selected_row_data
        self.id, self.component, self.description, self.solution, self.document, self.root, self.edit, self.user, self.data = data
        print("id: ", self.id)
        print("component: ", self.component)
        print("problem: ", self.description)
        print("solution: ", self.solution)
        print("document: ", self.document)
        print("root: ", self.root)
        print("edit: ", self.edit)
        print("user: ", self.user)
        print("data: ", self.data)

        self.grab_set()
        self.title(f"Dettaglio problema # {self.id}")
        self.center_win_detail(1000, 800)
        self.resizable(False, False)

        log("INFO", f"USER={self.user} Aperta finestra dettaglio del record ID[{self.id}]")

        # Configurazione griglia principale
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # ======================= FRAME SUPERIORE PER COMPONENTE/AUTORE/DATA =======================
        self.upper_frame = ctk.CTkFrame(self, corner_radius=4)
        self.upper_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        self.upper_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Componente, utente e data di rilevazione del problema
        self.label_component_description = ctk.CTkLabel(master=self.upper_frame, 
                                                        text=f"Componente: {self.component}", 
                                                        font=("Roboto", 18, "bold"),
                                                        wraplength=600
                                                        )
        self.label_component_description.grid(row=0, column=0, padx=10, pady=10, sticky="nw")
        self.user_label = ctk.CTkLabel(master=self.upper_frame, 
                                       text=f"Utente: {self.user}", 
                                       font=("Roboto", 14, "bold")
                                       )
        self.user_label.grid(row=0, column=1, padx=10, pady=10, sticky="ne")
        self.data_label = ctk.CTkLabel(master=self.upper_frame, 
                                       text=f"Data: {self.data}", 
                                       font=("Roboto", 14, "bold")
                                       )
        self.data_label.grid(row=0, column=2, padx=10, pady=10, sticky="ne")

        # ======================= FRAME INFERRIORE PER DETTAGLI/PULSANTI ===========================
        self.bottom_frame = ctk.CTkFrame(self, corner_radius=4)
        self.bottom_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.bottom_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.bottom_frame.grid_rowconfigure((2, 4), weight=1)

        # Descrizione dettagliata del problema
        self.label_win_description = ctk.CTkLabel(master=self.bottom_frame, 
                                                  text="Descrizione del problema", 
                                                  font=("Roboto", 18, "bold")
                                                  )
        self.label_win_description.grid(row=1, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="nw")
        self.text_win_description_detail = ctk.CTkTextbox(master=self.bottom_frame, 
                                                          font=("Roboto", 15), 
                                                          fg_color=self.master.button_fg_color
                                                          )
        self.text_win_description_detail.grid(row=2, column=0, columnspan=3, padx=0, pady=(0, 10), sticky="nsew")
        self.text_win_description_detail.insert("0.0", self.description)
        self.text_win_description_detail.configure(state="disabled")

        # Descrizione dettagliata della soluzione
        self.label_win_solution = ctk.CTkLabel(master=self.bottom_frame, 
                                               text="Soluzione e note", 
                                               font=("Roboto", 18, "bold")
                                               )
        self.label_win_solution.grid(row=3, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="nw")
        self.text_win_solution_detail = ctk.CTkTextbox(master=self.bottom_frame, 
                                                       font=("Roboto", 15), 
                                                       fg_color=self.master.button_fg_color
                                                       )
        self.text_win_solution_detail.grid(row=4, column=0, columnspan=3, padx=0, pady=(0, 10), sticky="nsew")
        self.text_win_solution_detail.insert("0.0", self.solution)
        self.text_win_description_detail.configure(state="disabled")

        # pulsante edita
        self.button_edit = ctk.CTkButton(master=self.bottom_frame, 
                                             text="Edita record 📝", 
                                             font=("Roboto", 15), 
                                             command=self.edit_record
                                             )
        self.button_edit.grid(row=5, column=0, padx=10, pady=10, sticky="new")

        # pulsante per aprire il doc ma solo se presente (quindi non messo in grid)
        self.button_view_doc = ctk.CTkButton(master=self.bottom_frame, 
                                                 text="Apri allegato 📄", 
                                                 font=("Roboto", 15), 
                                                 command=self.view_document
                                                 )
        
        # pulsante per aggiungere/cambiare un documento solo se NON presente (quindi non messo in grid)
        self.button_add_doc = ctk.CTkButton(master=self.bottom_frame, 
                                                text="Cambia allegato 🆕", 
                                                font=("Roboto", 15), 
                                                command=self.add_document
                                                )
        self.button_add_doc.grid(row=5, column=2, padx=10, pady=10, sticky="new")

        # pulsante elimina record
        self.button_delete_record = ctk.CTkButton(master=self.bottom_frame, 
                                                  text="Elimina record 🗑️", 
                                                  font=("Roboto", 15), 
                                                  fg_color="red", 
                                                  hover_color="#C82333", 
                                                  command=self.open_delete_window
                                                  )
        self.button_delete_record.grid(row=6, column=0, columnspan=1, padx=10, pady=10, sticky="sew")

        # pulsante chiudi finestra
        self.button_close_win = ctk.CTkButton(master=self.bottom_frame, 
                                                  text="Chiudi la finestra ❌", 
                                                  font=("Roboto", 15), 
                                                  fg_color="red", 
                                                  hover_color="#C82333", 
                                                  command=self.destroy
                                                  )
        self.button_close_win.grid(row=6, column=2, columnspan=1, padx=10, pady=10, sticky="sew")

        # Pulsante visualizza documento, edita record e chiudi finestra
        if self.document == "Si":
            self.button_view_doc.grid(row=5, column=1, columnspan=1, padx=10, pady=10, sticky="new")
            self.button_add_doc.configure(text="Cambia allegato 🆕")
        else:
            self.button_add_doc.configure(text="Aggiungi allegato 🆕")

        # Necessario per portare la finestra in primo piano
        self.after(100, self.lift)

    # Funzione per visualizzare il documento allegato
    def view_document(self):
        try:
            if self.root != None:
                log("INFO", f"USER={self.user} Aperto documento allegato al record ID [{self.id}]")
                self.master.debug_message(f"Aperto documento allegato al record ID [{self.id}]")
                os.startfile(self.root)
        except FileNotFoundError as err:
            print(f"File non trovato!\n[Error]: {err}")
            log("WARNING", f"USER={self.user} Documento allegato al record ID [{self.id}] non trovato")
            self.master.debug_message(f"USER={self.user} Documento allegato al record ID [{self.id}] non trovato")
            msg = CTkMessagebox(
                title="File non trovato!",
                message="File non trovato!\nPotrebbe essere stato rinominato o eliminato dalla cartella",
                icon="cancel",
                border_width=2,
                border_color="red",
                option_1="Ok",
            )

            if msg.get() == "Ok":
                print("File non trovato - Modifica document=No")
                self.document = "No"
                self.root = None
                query.edit_record(self.id, self.component, self.description, self.solution, self.document, self.root, self.edit, self.user, self.data)
                self.master.load_data()
                return


    # Funzione per aggiungere un documento
    def add_document(self):
        current_data = (self.id, self.component, self.description, self.solution, self.document, self.root, self.edit, self.user, self.data)
        if self.document == "Si":
            DocumentExistAllert(self, current_data)
        else:
            DocumentNotExistAllert(self, current_data)

    # Funzione per editare il record
    def edit_record(self):
        number_editing_record = query.get_id_editing_record()
        if len(number_editing_record) >= 1:
            msg_edit_not_possible = CTkMessagebox(
                title="Editazione non possibile",
                message="Editazione non possibile: è già presente un record aperto in editazione",
                icon="warning",
                border_width=2,
                border_color="orange",
                option_1="Ok",
            )
            return
        
        log("INFO", f"USER={self.user} Apertura editazione del record ID [{self.id}]")
        self.master.button_save.grid(columnspan=1)
        self.master.button_cancel_editing.grid(column=1, row=7, padx=10, pady=10, sticky="ew")

        self.master.record_edit_id = self.id

        self.master.editing_actual_record = query.set_editing(self.id)
        self.master.show_edit_warning(self.id)

        self.master.record_edit_document = self.document
        self.master.record_edit_root = self.root
        component = self.component
        self.master.entry_component.insert("0", component)
        description = self.text_win_description_detail.get("1.0", "end-1c")
        self.master.text_description.insert("0.0", description)
        solution = self.text_win_solution_detail.get("1.0", "end-1c")
        self.master.text_solution.insert("0.0", solution) 
        self.destroy()
    
    # Funzione per aprire finestra di conferma cancellazione record
    def open_delete_window(self):
        if not self.master.selected_row_data:
            return
        
        # Se la riga è vuota non compare la finestra
        if self.selected_row_data[0] == ' ':
            return
        
        self.master.debug_message(f"USER={self.user} Apertura finestra di eliminazione record")
        CancelConfirm(self, self.master.selected_row_data)

    # Funzione per centrare la finestra di dettaglio all'apertura
    def center_win_detail(self, width, height):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        scale = self._get_window_scaling()

        x = int(((screen_width / 2) - (width / 2)) * scale)
        y = int(((screen_height / 2) - (height / 2)) * scale)
        self.geometry(f"{width}x{height}+{x}+{y}")