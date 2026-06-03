from tkinter import filedialog, TclError
from CTkMessagebox import CTkMessagebox
from CTkMenuBarPlus import ContextMenu
import customtkinter as ctk
from CTkTable import *
import shutil
import db
import query
import os
from detail_window import DetailWindow
from cancel_window import CancelConfirm

ctk.set_appearance_mode("System")   # imposta il tema del sistema
ctk.set_default_color_theme("blue") # imposta i colori sul blu
mode = ctk.get_appearance_mode()
documents_root = r"C:\BRETON\Appunti\Programmazione\Archivio Errori\documents"

# Classe della finestra principale
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Archivio Errori")
        self.center_win_app(1500, 830)
        self.resizable(True, True)

        # configurazione griglia principale
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ======================= FRAME DI SINISTRA =======================
        self.left_frame = ctk.CTkFrame(self, width=350, corner_radius=4)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.left_frame.grid_rowconfigure(8, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        # Label e Entry per inserimento del componente
        self.label_component = ctk.CTkLabel(self.left_frame, text="Componente", font=("Roboto", 16, "bold"))
        self.label_component.grid(column=0, row=0, padx=10, pady=10, sticky="nsw")
        self.entry_component = ctk.CTkEntry(self.left_frame, placeholder_text="Es. KEBA, B&R, Siemens...", corner_radius=4, font=("Roboto", 15))
        self.entry_component.grid(column=0, row=1, padx=10, pady=(0, 10), sticky="ew")

        # Label e Textbox per inserimento descrizione problema
        self.label_description = ctk.CTkLabel(self.left_frame, text="Descrizione problema", font=("Roboto", 16, "bold"))
        self.label_description.grid(column=0, row=2, padx=10, pady=10, sticky="nsw")
        self.text_description = ctk.CTkTextbox(self.left_frame, font=("Roboto", 15))
        self.text_description.grid(column=0, row=3, padx=10, pady=(0, 10), sticky="nsew")
        
        # Label e Textbox per inserimento soluzione problema
        self.label_solution = ctk.CTkLabel(self.left_frame, text="Soluzione e note", font=("Roboto", 16, "bold"))
        self.label_solution.grid(column=0, row=4, padx=10, pady=10, sticky="nsw")
        self.text_solution = ctk.CTkTextbox(self.left_frame, font=("Roboto", 15))
        self.text_solution.grid(column=0, row=5, padx=10, pady=(0, 10), sticky="nsew")

        # Pulsanti per allegare documenti, salvare il db, chiudere il programma
        #self.button_allega = ctk.CTkButton(master=self.left_frame, text="Allega documento 📁", font=("Roboto", 15), command=self.add_document)
        #self.button_allega.grid(column=0, row=6, padx=10, pady=10, sticky="ew")
        self.button_save = ctk.CTkButton(master=self.left_frame, text="Salva in database 💾", font=("Roboto", 15), fg_color="green", hover_color="#218838", command=self.insert_record)
        self.button_save.grid(column=0, row=7, padx=10, pady=10, sticky="ew")
        self.button_exit = ctk.CTkButton(master=self.left_frame, text="Esci dal programma ❌", font=("Roboto", 15), fg_color="red", hover_color="#C82333", command=self.quit)
        self.button_exit.grid(column=0, row=8 , padx=10, pady=10, sticky="sew")

        # ======================= FRAME DI DESTRA =======================
        self.right_frame = ctk.CTkFrame(self, corner_radius=4)
        self.right_frame.grid(row=0, padx=10, pady=10, column=1, sticky="nsew")
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # Entry della barra di ricerca
        self.search_entry = ctk.CTkEntry(self.right_frame, placeholder_text="🔎 Cerca", height=40, corner_radius=4, font=("Roboto", 18))
        self.search_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.search_entry.bind("<KeyRelease>", self.dynamic_search)

        # Frame con scroll-bar in cui inserire la tabella
        self.scrollable_frame = ctk.CTkScrollableFrame(self.right_frame, corner_radius=4)
        self.scrollable_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure((0, 1), weight=1)
        self.scrollable_frame.grid_rowconfigure((0, 1), weight=1)

        # Definizione della tabella, della sua header e delle dimensioni delle colonne
        headers = "      ID\t      Componente\t\t                 Problema\t\t\t\t                    Soluzione\t\t          Documento"
        self.header_table = ctk.CTkLabel(master=self.scrollable_frame, width=1150, corner_radius=4, text=headers, anchor="w",  font=("Roboto", 18, "bold"))
        self.header_table.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="ew")

        values = []
        self.value_table = CTkTable(master=self.scrollable_frame, row=100, column=5, width=1150, corner_radius=4, values=values, hover=True, command=self.handle_table_click)
        self.value_table.edit_column(0, width=100)
        self.value_table.edit_column(1, width=200)
        self.value_table.edit_column(2, width=350)
        self.value_table.edit_column(3, width=350)
        self.value_table.edit_column(4, width=150)
        self.value_table.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="ew")

        self.load_data()

        self.value_table.bind("<Double-1>", self.handle_double_click)
        self.selected_row_data = None
        self.record_edit_id = None
        self.record_edit_document = None
        self.record_edit_root = None

        # Pulsante per rimuovere il record selezionato della tabella
        self.button_remove = ctk.CTkButton(master=self.right_frame, text="Elimina record 🗑️", font=("Roboto", 15), fg_color="red", hover_color="#C82333", command=self.open_delete_window)
        self.button_remove.grid(column=0, row=2, padx=10, pady=10, sticky="ew")

    # Funzione per aprire finestra di conferma cancellazione record
    def open_delete_window(self):
        if not self.selected_row_data:
            print("Nessuna riga selezionata")
            return
        
        # Se la riga è vuota non compare la finestra
        if self.selected_row_data[0] == ' ':
            print("Riga vuota")
            return
        
        CancelConfirm(self, self.selected_row_data)

    # Funzione per centrare la finestra nello schermo
    def center_win_app(self, width, height):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        scale = self._get_window_scaling()

        x = int(((screen_width / 2) - (width / 2)) * scale)
        y = int(((screen_height / 2) - (height / 2)) * scale)
        self.geometry(f"{width}x{height}+{x}+{y}")

    # Funzione "intelligente" per gestire i click sui record della tabella
    def handle_table_click(self, event):
        try:
            row = event["row"]
            # se il click è sulla riga 0 di indice si ignora
            if row < 0:
                return
            
            # Deseleziona tutto prima di una nuova selezione, ciclo che evita l'accumulo di selezioni
            for i in range(self.value_table.rows):
                self.value_table.deselect_row(i)

            self.selected_row_data = None
            # Selezione della riga corrente
            self.value_table.select_row(row)
            # Salva i dati della riga selezionata
            self.selected_row_data = self.full_data[row]
        except:
            return
    
    # Funzione per l'apertura della finestra al doppio click
    def handle_double_click(self, event):
        # Recupera riga seleizonata
        if not self.selected_row_data:
            return
        
        # Se la riga è vuota non compare la finestra
        if self.selected_row_data[0] == ' ':
            print("Riga vuota")
            return
        
        DetailWindow(self, self.selected_row_data)

    # Funzione per formattare i dati del database in liste di liste per la CTkTable
    def format_data(self, rows):
        formatted_data = []

        for row in rows:
            formatted_data.append([row['ID'], 
                                  row['Componente'], 
                                  row['Problema'], 
                                  row['Soluzione'], 
                                  row['Documentazione'],
                                  row['Percorso']])
        
        return formatted_data

    # Funzione per caricare i dati del database dentro alla tabella
    def load_data(self, search_text=None):
        # se viene scritto qualcosa nella barra si carica la tabella di ricerca
        if search_text and search_text.strip() != "":
            raw_rows = query.search(search_text)
        else:
            raw_rows = query.get_database()                  # lista di dizionari (coppie key-value)
            #values = self.format_data(raw_rows)             # lista di liste (solo valori)

        self.full_data = self.format_data(raw_rows)
        # Solo prime 5 colonne per la tabella
        visible_values = [row[:5] for row in self.full_data]
        self.value_table.values = visible_values
        self.value_table.update_values(visible_values)
        self.selected_row_data = None
        print(f"TEST: Record trovati: {len(raw_rows)}")

    # Funzione per leggere il contenuto dei Textbox (frame di sinistra)
    def insert_record(self):
        # self.load_data()
        raw_row = query.get_max_id()
        current_id = raw_row[0]["ID"]

        component = self.entry_component.get().strip()
        description = self.text_description.get("1.0", "end-1c").strip()
        document = ""
        solution = self.text_solution.get("1.0", "end-1c").strip()
        root = None

        if self.record_edit_id is not None:
            id = self.record_edit_id
            document = self.record_edit_document
            root = self.record_edit_root
            query.edit_record(id, component, description, solution, document, root)
            self.record_edit_id = None
            self.load_data()

            self.entry_component.delete("0", "end")
            self.text_description.delete("0.0", "end")
            self.text_solution.delete("0.0", "end")
        else:
            # Calcola ID del nuovo record e legge le entry
            id = int(current_id) + 1

            # Messaggio per chiedere se si vuole allegare un file
            msg = CTkMessagebox(
                title="Allega file",
                message="Vuoi allegare un file al record?",
                icon="info",
                option_1="Si",
                option_2="No",
                justify="center"
            )

            # Se non si vuole aggiungere un file
            if msg.get() == "No":
                print("Non voglio aggiungere")
                document = "No"
                query.insert_record(id, component, description, solution, document, root)
                self.load_data()
                self.entry_component.delete("0", "end")
                self.text_description.delete("0.0", "end")
                self.text_solution.delete("0.0", "end")
                return
            
            # Apre file explorer: restituisce il percorso in stringa se seleziona file, altrimenti stringa vuota 
            selected_file = filedialog.askopenfilename(title="Seleziona un file", filetypes=[("Tutti i file", "*.*")])

            # Se si clicca "Si" ma non si seleziona nessun file
            if not selected_file:
                print("File non selezionato")
                document = "No"
                query.insert_record(id, component, description, solution, document, root)
                self.load_data()
                self.entry_component.delete("0", "end")
                self.text_description.delete("0.0", "end")
                self.text_solution.delete("0.0", "end")
                return
            
            filename = os.path.basename(selected_file)  # estrae l'ultimo componente da un percorso (qui è nome file)
            destination_path = os.path.join(documents_root, filename)   # combina segmenti creando il percorso con separatori
            
            # Verifica se il percorso esiste, restituisce True o False
            if not os.path.isfile(destination_path):
                print("File nuovo")
                shutil.copy(selected_file, documents_root)  # copia file al percorso
                document = "Si"
                root = destination_path
                query.insert_record(id, component, description, solution, document, root)
                self.load_data()
                self.entry_component.delete("0", "end")
                self.text_description.delete("0.0", "end")
                self.text_solution.delete("0.0", "end")
                return
            
            # Messaggio che avvisa di file con stesso nome già presente
            msg_exist = CTkMessagebox(
                title="File esistente", 
                message=f'Esiste già un file "{filename}".\nVuoi sovrascriverlo?', 
                icon="warning", 
                option_1="Si", 
                option_2="No",
                justify="center"
            )

            if msg_exist.get() == "No":
                print("Non voglio sovrascrivere")
                document = "No"
                query.insert_record(id, component, description, solution, document, root)
                self.load_data()
                self.entry_component.delete("0", "end")
                self.text_description.delete("0.0", "end")
                self.text_solution.delete("0.0", "end")
                return
            
            # Se si vuole sovrascrivere
            shutil.copy(selected_file, destination_path)    # copia file al percorso
            print("File sovrascritto")
            document = "Si"
            root = destination_path
            query.insert_record(id, component, description, solution, document, root)
            self.load_data()

            self.entry_component.delete("0", "end")
            self.text_description.delete("0.0", "end")
            self.text_solution.delete("0.0", "end")
    
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
            return              # interruzione di esecuzione
        
        # event non è None, utente ha smesso di digitare e si cattura il testo
        text = self.search_entry.get().strip()
        # aggiorna la tabella quando sono finiti altri processi 
        self.after_idle(lambda: self.load_data(search_text=text))
        # reset del timer pronto per la prossima ricerca
        self.search_timer = None



if __name__ == "__main__":
    db.create_table()
    app = App()
    app.mainloop()