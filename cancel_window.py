import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import os
import query

# Classe per la finestra di conferma cancellazione record
class CancelConfirm(ctk.CTkToplevel):
    def __init__(self, master, data):
        super().__init__(master)
        
        self.id, self.component, self.problem, self.solution, self.document, self.root, self.edit, self.user, self.data = data
        self.master = master

        self.grab_set()
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
        self.label_cancel_confirm = ctk.CTkLabel(master=self.cancel_win_frame, 
                                                 text=f"Il record {self.id} verrà cancellato definitivamente.\nVerrà cancellato anche l'eventuale file allegato!\n\nConfermi la cancellazione?", font=("Roboto", 15))
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
        row = query.get_dettaglio(self.id)
        document = row[0]["Percorso"]
        if document != None:
            self.delete_document(document)
        
        query.delete_record(self.id)
        self.master.load_data()
        self.destroy()
    
    # Funzione per eliminare il documento allegato
    def delete_document(self, document):
        if os.path.isfile(document):
            os.remove(document)
            print(f"Documento {document} rimosso")
            return

        msg = CTkMessagebox(title="Not found",
                            message="Documento non trovato",
                            icon="warning",
                            option_1="Ok",
                            justify="center")
        print("Documento non trovato")