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
from app_left import LeftPanel
from app_right import RightPanel
from theme import THEMES

ctk.set_appearance_mode("System")   # imposta il tema del sistema
ctk.set_default_color_theme("blue") # imposta i colori sul blu
mode = ctk.get_appearance_mode()
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

        self.documents_root = r"Documents"   # root salvataggio degli allegati

        # Selezione del tema in base al tema del sistema operativo
        self.theme_name = ctk.get_appearance_mode()
        self.theme = THEMES[self.theme_name]

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
        #file_dropdown.add_option(option="Esci", command=self.left_panel.close_program)

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
        self.frame.pack(fill="both", expand=True, padx=0, pady=0)

        self.frame.grid_columnconfigure(0, weight=0)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)

        # ======================= FRAME DI SINISTRA =====================
        self.left_frame = ctk.CTkFrame(self.frame, width=350, corner_radius=4)
        self.left_frame.grid(row=0,column=0, padx=(10, 5), pady=10, sticky="nsew")
        self.left_frame.grid_rowconfigure(9, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_panel = LeftPanel(self.left_frame, self)
        self.protocol("WM_DELETE_WINDOW", self.left_panel.close_program)

        #self.show_edit_warning(self.record_edit_id) # verifica se ci sono record in editazione
        self.update()                               # aggiorna la finestra per visualizzare il messaggio record in editazione

        # ======================= FRAME DI DESTRA =======================
        self.right_frame = ctk.CTkFrame(self.frame, corner_radius=4)
        self.right_frame.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_panel = RightPanel(self.right_frame, self)
        self.right_panel.load_data()

        # Funzione per chiudere la finestra di splash screen se presente
        try:
            import pyi_splash   # type: ignore
            pyi_splash.close()
        except ImportError:
            pass

        # ====================== FINE INIZIALIZZAZIONE DELLA FINESTRA PRINCIPALE ======================


    # Funzione per applicare il tema selezionato al programma
    def apply_theme(self):
        # Applicazione temi della tabella
        self.right_panel.style.configure(
            "Treeview.Heading",
            background=self.theme["BG_COLOR_HEADING"],
            foreground=self.theme["FG_COLOR"]
        )
        self.right_panel.style.configure(
            "Treeview",
            background=self.theme["BG_COLOR_TREEVIEW"],
            foreground=self.theme["FG_COLOR"],
            fieldbackground=self.theme["BG_COLOR_TREEVIEW"]
        )
        self.right_panel.value_table.tag_configure("pari", background=self.theme["BG_COLOR_TREEVIEW"])
        self.right_panel.value_table.tag_configure("dispari", background=self.theme["BG_COLOR_TREEVIEW_ALTERNATE"])

        # Applicazione temi dei pulsanti
        self.left_panel.description_editor_button.configure(
            text_color=self.theme["BUTTON_COLOR"],
            fg_color=self.theme["BUTTON_FG_COLOR"],
            hover_color=self.theme["BUTTON_HOVER_COLOR"]
        )
        self.left_panel.solution_editor_button.configure(
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