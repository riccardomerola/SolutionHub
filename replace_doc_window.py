import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from tkinter import filedialog
from logger import log
import query
import os
import shutil


# Classe per la finestra che compare aggiungendo un doc su record in cui è presente un doc
class DocumentExistAllert(ctk.CTkToplevel):
    def __init__(self, master, data):
        super().__init__(master)

        self.id, self.sector, self.element, self.description, self.solution, self.document, self.root, self.edit, self.user, self.data = data
        self.master = master

        self.grab_set()
        self.title("Documento già esistente")
        self.center_document_exist_win(450, 250)
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ======================= FRAME =======================
        self.document_exist_win_frame = ctk.CTkFrame(self, corner_radius=4)
        self.document_exist_win_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.document_exist_win_frame.grid_columnconfigure(0, weight=1)
        self.document_exist_win_frame.grid_rowconfigure((0, 1, 2), weight=1)

        self.label_document_exist = ctk.CTkLabel(
            master=self.document_exist_win_frame,
            text="Per questo record è già presente un documento.\nVuoi sostituirlo?",
            font=("Roboto", 17, "bold")
        )
        self.label_document_exist.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.button_replace_document = ctk.CTkButton(
            master=self.document_exist_win_frame,
            text="Sostituisci documento ⬅️",
            font=("Roboto", 15),
            command=self.change_document
        )
        self.button_replace_document.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.button_close_win_document = ctk.CTkButton(
            master=self.document_exist_win_frame,
            text="Chiudi la finestra ❌",
            font=("Roboto", 15),
            fg_color="red",
            hover_color="#C82333",
            command=self.destroy
        )
        self.button_close_win_document.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="new")

        self.attributes("-topmost", True)
        self.after(10, self.grab_set)
        self.after(10, self.focus_force)

    # Funzione per centrare la finestra nello schermo
    def center_document_exist_win(self, width, height):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight() - 80
        scale = self._get_window_scaling()

        x = int(((screen_width / 2) - (width / 2)) * scale)
        y = int(((screen_height / 2) - (height / 2)) * scale)
        self.geometry(f"{width}x{height}+{x}+{y}")

    # Funzione pre sostituire il documento già presente
    def change_document(self):
        from main import documents_root
        self.master.destroy()
        self.destroy()
        data = query.get_dettaglio(self.id)
        print(data)

        msg_warning = CTkMessagebox(
            title="ATTENZIONE",
            message="Questa oprazione elimina il file attuale\nVuoi sostituire il file attuale?",
            icon="warning",
            border_width=2,
            border_color="orange",
            option_1="Si",
            option_2="No",
            justify="center"
        )

        if msg_warning.get() == "No":
            print("Non voglio cambiare il file")
            self.master.master.debug_message(f'Sostituzione del documento allegato al record ID[{self.id}] annullata')
            self.destroy()
            return

        selected_file = filedialog.askopenfilename(title="Seleziona un file", filetypes=[("Turi i file", "*.*")])
        file = os.path.basename(selected_file)
        filename = f"{self.id}_{file}"
        destination_path = os.path.join(documents_root, filename)
        try:
            if not os.path.isfile(destination_path):
                print("Nuovo file")
                shutil.copy(selected_file, destination_path)
                self.root = destination_path
                query.edit_record(self.id, self.sector, self.element, self.description, self.solution, self.document, self.root, self.edit, self.user, self.data)
                log("INFO", f'USER={self.user} Aggiunto nuovo documento "{filename}" allegato al record ID [{self.id}]')
                self.master.master.debug_message(f'Aggiunto un nuovo documento allegato al record ID[{self.id}]')
                self.master.master.load_data()
                return

            msg_exist = CTkMessagebox(
                title="File esistete",
                message=f'Esiste già un file "{filename}" relativo al record ID[{self.id}].\nVuoi sovrascriverlo?',
                icon="warning",
                border_width=2,
                border_color="orange",
                option_1="Si",
                option_2="No",
                justify="center"
            )

            if msg_exist.get() == "No" or msg_exist.get() == None:
                print("Non voglio sovrascrivere")
                self.master.master.debug_message(f'Documento allegato al record ID[{self.id}] non inserito')
                self.destroy()
            else:
                shutil.copy(selected_file, destination_path)
                print("File sovrascritto")
                self.root = destination_path
                query.edit_record(self.id, self.sector, self.element, self.description, self.solution, self.document, self.root, self.edit, self.user, self.data)
                log("INFO", f'USER={self.user} Sovrascritto documento allegato al record ID [{self.id}]. Nuovo documento: "{filename}"')
                self.master.master.debug_message(f'Aggiunto un documento allegato al record ID[{self.id}] (sovrascritto vecchio documento)')
                self.master.master.load_data()
                return

        except FileNotFoundError as err:
            print(f"Errore: {err}")
            self.destroy()