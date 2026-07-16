import customtkinter as ctk

# Classe per l'espansione dei textbox
class LargeTextEditor(ctk.CTkToplevel):
    def __init__(self, master, source_textbox):
        super().__init__(master)

        self.source_textbox = source_textbox

        self.grab_set()
        self.title("Text editor")
        self.center_win_editor(1000, 700)
        self.resizable(True, True)

        # Configurazione griglia principale
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ======================= FRAME =======================
        self.text_frame = ctk.CTkFrame(self, corner_radius=4)
        self.text_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.text_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.text_frame.grid_rowconfigure(1, weight=1)

        # Creazione nuovo Textbox più grande + pulsanti salvataggio
        self.label_editor = ctk.CTkLabel(
            self.text_frame,
            text="Text Editor",
            font=("Roboto", 18, "bold")
        )
        self.label_editor.grid(column=0, row=0, padx=10, pady=10, sticky="nw")
        self.large_textbox = ctk.CTkTextbox(
            self.text_frame,
            height=500,
            width=800,
            font=("Roboto", 15)
        )
        self.large_textbox.grid(column=0, row=1, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.save_button = ctk.CTkButton(
            self.text_frame,
            text="Salva 💾",
            font=("Roboto", 15),
            command=self.save_text
        )
        self.save_button.grid(column=0, row=2, padx=10, pady=10, sticky="ew")
        self.exit_button = ctk.CTkButton(
            self.text_frame,
            text="Chiudi ❌",
            font=("Roboto", 15),
            command=self.destroy
        )
        self.exit_button.grid(column=2, row=2, padx=10, pady=10, sticky="ew")

        # Inserimento del testo della textbox piccola nell'editor
        text = self.source_textbox.get("1.0", "end-1c").strip()
        self.large_textbox.insert("1.0", text)

        # Necessario per portare la finestra in primo piano
        self.after(100, self.lift)

        # ======================== FINE INIZIALIZZAZIONE DELLA FINESTRA =======================


    # Funzione per riportare il testo nel textbox piccolo pronto per essere salvato
    def save_text(self):
        text = self.large_textbox.get("0.0", "end-1c").strip()
        self.source_textbox.delete("1.0", "end")
        self.source_textbox.insert("1.0", text)
        self.destroy()


    # Funzione per centrare la finestra di dettaglio all'apertura
    def center_win_editor(self, width, height):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight() - 80
        scale = self._get_window_scaling()

        x = int(((screen_width / 2) - (width / 2)) * scale)
        y = int(((screen_height / 2) - (height / 2)) * scale)
        self.geometry(f"{width}x{height}+{x}+{y}")