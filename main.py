import customtkinter as ctk
from CTkTable import *
import db
import query

ctk.set_appearance_mode("System")   # imposta il tema del sistema
ctk.set_default_color_theme("blue") # imposta i colori sul blu
mode = ctk.get_appearance_mode()

# Classe della finestra principale
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Archivio Errori")
        self.center_win_app(1500, 830)
        self.resizable(False, False)

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
        self.button_allega = ctk.CTkButton(master=self.left_frame, text="Allega documento 📁", font=("Roboto", 15))
        self.button_allega.grid(column=0, row=6, padx=10, pady=10, sticky="ew")
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
        self.selected_row_data = self.value_table.get_row(row)
    
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
                                  row['Documentazione']])
        
        return formatted_data

    # Funzione per caricare i dati del database dentro alla tabella
    def load_data(self):
        raw_rows = query.get_database()                 # lista di dizionari (coppie key-value)
        values = self.format_data(raw_rows)             # lista di liste (solo valori)

        self.value_table.values = values
        self.value_table.update_values(values)

        self.selected_row_data = None

    # Funzione per leggere il contenuto dei Textbox (frame di sinistra)
    def insert_record(self):
        self.load_data()
        raw_row = query.get_max_id()
        current_id = raw_row[0]["ID"]

        id = int(current_id) + 1
        component = self.entry_component.get().strip()
        description = self.text_description.get("1.0", "end-1c").strip()
        solution = self.text_solution.get("1.0", "end-1c").strip()
        document = "No"

        query.insert_record(id, component, description, solution, document)
        self.load_data()

        self.entry_component.delete("0", "end")
        self.text_description.delete("0.0", "end")
        self.text_solution.delete("0.0", "end")
        

# Classe della finestra di dettaglio
class DetailWindow(ctk.CTkToplevel):
    def __init__(self, master, data):
        super().__init__(master)

        self.id, self.component, self.problem, self.solution, self.document = data

        self.title(f"Dettaglio problema # {self.id}")
        self.center_win_detail(500, 450)
        self.resizable(False, False)

        # Configurazione griglia principale
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ======================= FRAME =======================
        self.win_frame = ctk.CTkFrame(self, corner_radius=4)
        self.win_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.win_frame.grid_columnconfigure((0, 1), weight=1)
        self.win_frame.grid_rowconfigure((1, 3), weight=1)

        # Descrizione dettagliata del problema
        color = "#DBDBDB" if mode == 'Light'else "#2B2B2B"
        self.label_win_description = ctk.CTkLabel(master=self.win_frame, text="Descrizione del problema", font=("Roboto", 18, "bold"))
        self.label_win_description.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="nw")
        self.text_win_description_detail = ctk.CTkTextbox(master=self.win_frame, font=("Roboto", 15), fg_color=color)
        self.text_win_description_detail.grid(row=1, column=0, columnspan=2, padx=0, pady=(0, 10), sticky="nsew")
        self.text_win_description_detail.insert("0.0", self.problem)
        self.text_win_description_detail.configure(state="disabled")

        # Descrizione dettagliata della soluzione
        self.label_win_solution = ctk.CTkLabel(master=self.win_frame, text="Descrizione della soluzione", font=("Roboto", 18, "bold"))
        self.label_win_solution.grid(row=2, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="nw")
        self.text_win_solution_detail = ctk.CTkTextbox(master=self.win_frame, font=("Roboto", 15), fg_color=color)
        self.text_win_solution_detail.grid(row=3, column=0, columnspan=2, padx=0, pady=(0, 10), sticky="nsew")
        self.text_win_solution_detail.insert("0.0", self.solution)
        self.text_win_description_detail.configure(state="disabled")

        # Pulsante visualizza documento e chiudi finestra
        self.button_view_doc = ctk.CTkButton(master=self.win_frame, text="Visualizza documento 📄", font=("Roboto", 15))
        self.button_view_doc.grid(row=4, column=0, padx=10, pady=10, sticky="new")
        self.button_add_doc = ctk.CTkButton(master=self.win_frame, text="Aggiungi documento 🆕", font=("Roboto", 15), command=self.add_document)
        self.button_add_doc.grid(row=4, column=1, padx=10, pady=10, sticky="new")
        self.button_close_win = ctk.CTkButton(master=self.win_frame, text="Chiudi la finestra ❌", font=("Roboto", 15), fg_color="red", hover_color="#C82333", command=self.destroy)
        self.button_close_win.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="sew")

        # Necessario per portare la finestra in primo piano
        self.after(100, self.lift)

    # Funzione per aggiungere un documento
    def add_document(self):
        print(self.document)
        if self.document == "Si":
            DocumentExistAllert(self)
        else:
            DocumentNotExistAllert(self)

    # Funzione per centrare la finestra di dettaglio all'apertura
    def center_win_detail(self, width, height):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        scale = self._get_window_scaling()

        x = int(((screen_width / 2) - (width / 2)) * scale)
        y = int(((screen_height / 2) - (height / 2)) * scale)
        self.geometry(f"{width}x{height}+{x}+{y}")


# Classe per la finestra di conferma cancellazione record
class CancelConfirm(ctk.CTkToplevel):
    def __init__(self, master, data):
        super().__init__(master)
        
        self.id, self.component, self.problem, self.solution, self.document = data
        self.master = master

        self.title("Conferma cancellazione")
        self.center_cancell_win(400, 350)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ======================= FRAME =======================
        self.cancel_win_frame = ctk.CTkFrame(self, corner_radius=4)
        self.cancel_win_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.cancel_win_frame.grid_columnconfigure((0, 1), weight=1)
        self.cancel_win_frame.grid_rowconfigure((0, 1, 2), weight=1)

        # Label di attenzione
        self.label_cancel = ctk.CTkLabel(master=self.cancel_win_frame, text="⚠️ ATTENZIONE ⚠️", font=("Roboto", 18, "bold"), text_color="red")
        self.label_cancel.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.label_cancel_confirm = ctk.CTkLabel(master=self.cancel_win_frame, text=f"Il record {self.id} verrà cancellato definitivamente.\nConfermi la cancellazione?", font=("Roboto", 15))
        self.label_cancel_confirm.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Pulsanti di conferma cancellazione o chiudi finestra (senza cancellare record)
        self.button_delete_record = ctk.CTkButton(master=self.cancel_win_frame, text="      Cancella record 🗑️", font=("Roboto", 15), fg_color="red", hover_color="#C82333", command=self.delete_record)
        self.button_delete_record.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.button_back = ctk.CTkButton(master=self.cancel_win_frame, text="Annulla operazione ↩️", font=("Roboto", 15), command=self.destroy)
        self.button_back.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        self.attributes("-topmost", True)
        self.after(10, self.grab_set)
        self.after(10, self.focus_force)

    # Funzione per centrare la finestra nello schermo
    def center_cancell_win(self, width, height):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        scale = self._get_window_scaling()

        x = int(((screen_width / 2) - (width / 2)) * scale)
        y = int(((screen_height / 2) - (height / 2)) * scale)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    # Funzione per eliminare il record dal database
    def delete_record(self):
        query.delete_record(self.id)
        self.master.load_data()
        self.destroy()
        


# Classe per la finestra di conferma cancellazione record
class DocumentExistAllert(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Documento già esistente")
        self.center_document_exist_win(450, 250)
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ======================= FRAME =======================
        self.document_exist_win_frame = ctk.CTkFrame(self, corner_radius=4)
        self.document_exist_win_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.document_exist_win_frame.grid_columnconfigure(0, weight=1)
        self.document_exist_win_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)

        self.label_document_exist = ctk.CTkLabel(master=self.document_exist_win_frame, text="Per questo record è già presente un documento.\nVuoi sostituirlo?", font=("Roboto", 17, "bold"))
        self.label_document_exist.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.button_view_document = ctk.CTkButton(master=self.document_exist_win_frame, text="Visualizza documento 📄", font=("Roboto", 15))
        self.button_view_document.grid(row=1, column=0, padx=10, pady=10, sticky="sew")
        self.button_replace_document = ctk.CTkButton(master=self.document_exist_win_frame, text="Sostituisci documento ↩️", font=("Roboto", 15))
        self.button_replace_document.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.button_close_win_document = ctk.CTkButton(master=self.document_exist_win_frame, text="Chiudi la finestra ❌", font=("Roboto", 15), fg_color="red", hover_color="#C82333", command=self.destroy)
        self.button_close_win_document.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="new")

        self.attributes("-topmost", True)
        self.after(10, self.grab_set)
        self.after(10, self.focus_force)

    # Funzione per centrare la finestra nello schermo
    def center_document_exist_win(self, width, height):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        scale = self._get_window_scaling()

        x = int(((screen_width / 2) - (width / 2)) * scale)
        y = int(((screen_height / 2) - (height / 2)) * scale)
        self.geometry(f"{width}x{height}+{x}+{y}")


class DocumentNotExistAllert(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Documento non esistente")
        self.center_document_exist_win(450, 250)
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ======================= FRAME =======================
        self.document_not_exist_win_frame = ctk.CTkFrame(self, corner_radius=4)
        self.document_not_exist_win_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.document_not_exist_win_frame.grid_columnconfigure(0, weight=1)
        self.document_not_exist_win_frame.grid_rowconfigure((0, 1, 2), weight=1)

        self.label_document_not_exist = ctk.CTkLabel(master=self.document_not_exist_win_frame, text="Per questo record NON è presente un documento.\nVuoi aggiungerlo?", font=("Roboto", 17, "bold"))
        self.label_document_not_exist.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.button_add_document = ctk.CTkButton(master=self.document_not_exist_win_frame, text="Aggiungi documento 📄", font=("Roboto", 15))
        self.button_add_document.grid(row=1, column=0, padx=10, pady=10, sticky="sew")
        self.button_close_win_document = ctk.CTkButton(master=self.document_not_exist_win_frame, text="Chiudi la finestra ❌", font=("Roboto", 15), fg_color="red", hover_color="#C82333", command=self.destroy)
        self.button_close_win_document.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="new")

        self.attributes("-topmost", True)
        self.after(10, self.grab_set)
        self.after(10, self.focus_force)

    # Funzione per centrare la finestra nello schermo
    def center_document_exist_win(self, width, height):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        scale = self._get_window_scaling()

        x = int(((screen_width / 2) - (width / 2)) * scale)
        y = int(((screen_height / 2) - (height / 2)) * scale)
        self.geometry(f"{width}x{height}+{x}+{y}")

if __name__ == "__main__":
    db.create_table()
    app = App()
    app.mainloop()