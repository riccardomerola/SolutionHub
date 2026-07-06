import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from logger import log
import query
import os
import win32com.client as win32

# Classe della barra di menu
class MenuBar():
    def __init__(self, master):
        super().__init__()

        self.master = master
        self.debug_console_visible = False

    def change_database(self):
        print("Cambio database")

    # Cambio del tema dell'app
    def view_theme_option(self):
        self.theme_window = ctk.CTkToplevel()
        self.theme_window.grab_set()
        self.theme_window.title("Modifica il tema del software")
        self.theme_window.resizable(False, False)

        # Centraggio della finestra di info
        self.center_win_detail(self.theme_window, 160, 150)

        # ---------------- Grafica della finestra ---------------- 
        frame_theme = ctk.CTkFrame(self.theme_window, corner_radius=4)
        frame_theme.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Tema iniziale dell'app
        original_theme = ctk.get_appearance_mode()
        self.radio_var = ctk.StringVar(master=frame_theme, value=original_theme)

        # radio button per selezione tema
        button_dark_theme = ctk.CTkRadioButton(frame_theme, 
                                               text="Tema scuro", 
                                               variable=self.radio_var, 
                                               value="Dark", 
                                               command=self.change_theme
                                               )
        button_dark_theme.pack(padx=20, pady=20)
        button_light_theme = ctk.CTkRadioButton(frame_theme, 
                                                text="Tema chiaro", 
                                                variable=self.radio_var, 
                                                value="Light", 
                                                command=self.change_theme
                                                )
        button_light_theme.pack(padx=20, pady=20)

    def change_theme(self):
        new_theme = self.radio_var.get()
        ctk.set_appearance_mode(new_theme)

        if new_theme == "Dark":
            self.master.bg_color_heading = "#2b2b2b"
            self.master.bg_color_treeview = "#2b2b2b"
            self.master.bg_color_treeview_alternate = "#343434"
            self.master.fg_color = "white"
            self.master.button_fg_color = "#2b2b2b"
            self.master.button_hover_color = "#3a3d3e"
            self.master.button_color = "white"
        else:
            self.master.bg_color_heading = "#e5e5e5"
            self.master.bg_color_treeview = "#f9f9f9"
            self.master.bg_color_treeview_alternate = "#f0f0f0"
            self.master.fg_color = "black"
            self.master.button_fg_color = "#dbdbdb"
            self.master.button_hover_color = "#cfcfcf"
            self.master.button_color = "black"
        
        self.master.style.configure("Treeview.Heading", 
                                    background=self.master.bg_color_heading if hasattr(self.master, 'right_frame') else self.master.bg_color_heading, 
                                    foreground=self.master.fg_color)
        self.master.style.configure("Treeview", 
                                    background=self.master.bg_color_treeview, 
                                    foreground=self.master.fg_color, 
                                    fieldbackground=self.master.bg_color_treeview)
        
        # Aggiorna i tag e ricarica i dati della TreeView (anch'essa sulla classe principale)
        self.master.value_table.tag_configure("pari", background=self.master.bg_color_treeview)
        self.master.value_table.tag_configure("dispari", background=self.master.bg_color_treeview_alternate)

        self.master.button_expand_description.configure(text_color=self.master.button_color, 
                                                        fg_color=self.master.button_fg_color, 
                                                        hover_color=self.master.button_hover_color)
        self.master.button_expand_problem.configure(text_color=self.master.button_color, 
                                                    fg_color=self.master.button_fg_color, 
                                                    hover_color=self.master.button_hover_color)
        
        # Forza il rinfresco visivo della tabella
        self.master.load_data()
        
        log("INFO", f"Tema dell'applicazione cambiato in {new_theme}")
        print(f"Tema aggiornato a {new_theme} dall'interno della classe secondaria")

    # Apertura del file .pdf con le istruzioni di utilizzo
    def open_instruction(self):
        root = r"C:\BRETON\Appunti\Programmazione\Archivio Errori\documents\Guida all'utilizzo.pdf"
        try:
            log("INFO", "Apertura file di Guida all'utilizzo")
            os.startfile(root)
        except FileNotFoundError as err:
            log("ERROR", f"Errore all'apertura del file Guida all'utilizzo: {err}")
            print(f"Guida all'utilizzo non trovato!\n[Error]: {err}")
            msg = CTkMessagebox(
                title="File non trovato!",
                message="Guida all'utilizzo non trovata!\nContatta l'amministratore",
                icon="cancel",
                border_width=2,
                border_color="red",
                option_1="Ok"
            )

            if msg.get() == "Ok":
                msg.destroy()

    # Apertura (e sotto chiusura) del frame di debug
    def open_debug(self):
        print("Apertura debug")
        log("INFO", "Apertura finestra di debug")
        if not self.debug_console_visible:
            self.master.frame_textbox.pack(pady=(0, 10), fill="x", side="bottom")
            self.debug_console_visible = True
        
    def close_debug(self):
        print("Chiudi debug")
        log("INFO", "Chiusura finestra di debug")
        self.master.frame_textbox.pack_forget()
        self.debug_console_visible = False

    # Apertura finestra in cui admin può resettare record in editazione in caso di chiusura forzata
    def reset_edit(self):
        self.reset_edit_window = ctk.CTkToplevel()
        self.reset_edit_window.grab_set()
        self.reset_edit_window.title("Reset dei record in editazione")
        self.reset_edit_window.resizable(False, False)
        self.center_win_detail(self.reset_edit_window, 350, 280)

        self.reset_edit_window.grid_columnconfigure(0, weight=1)

        # frame della finestra
        frame_reset_edit = ctk.CTkFrame(self.reset_edit_window, corner_radius=4)
        frame_reset_edit.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        frame_reset_edit.grid_columnconfigure(0, weight=1)

        user_label = ctk.CTkLabel(frame_reset_edit, text="Username: ", font=("Roboto", 16, "bold"))
        user_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsw")
        self.user_entry = ctk.CTkEntry(frame_reset_edit, 
                                  placeholder_text="Username...", 
                                  corner_radius=4, 
                                  font=("Roboto", 15)
                                  )
        self.user_entry.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        pwd_label = ctk.CTkLabel(frame_reset_edit, text="Password: ", font=("Roboto", 16, "bold"))
        pwd_label.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="nsw")
        self.pwd_entry = ctk.CTkEntry(frame_reset_edit, 
                                  placeholder_text="Password...", 
                                  corner_radius=4, 
                                  font=("Roboto", 15),
                                  show="*"
                                  )
        self.pwd_entry.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        self.message_label = ctk.CTkLabel(frame_reset_edit, text="")
        self.message_label.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
        confirm_button = ctk.CTkButton(frame_reset_edit, text="Conferma", font=("Roboto", 15), command=self.check_login)
        confirm_button.grid(row=5, column=0, padx=10, pady=10, sticky="nsew")

    # Funzione per verificare username e pwd per reset record in editazione
    def check_login(self):
        username = self.user_entry.get()
        password = self.pwd_entry.get()

        if username == "Relsoft" and password == "R3l50ft":
            self.message_label.configure(text="")
            msg = CTkMessagebox(
                title="Conferma di reset",
                message="Vuoi procedere con il reset dei record in editazione?",
                icon="warning",
                border_width=2,
                border_color="orange",
                option_1="Si",
                option_2="No",
                justify="center"
            ) 
            if msg.get() == "No" or msg.get() == None:
                self.reset_edit_window.destroy()
            else:
                query.reset_editazione()
                confirm_msg = CTkMessagebox(
                    title="Reset confermato",
                    message="Reset dei record in editazione avvenuto con successo",
                    icon="info",
                    border_width=2,
                    border_color="#0061FF",
                    option_1="Ok",
                    justify="center"
                )
                self.reset_edit_window.destroy()
                self.master.label_warning_edit.destroy()
                self.master.label_warning_edit = None
                log("INFO" , "Reset dei record bloccati in editazione")
                self.master.debug_message("Reset dei record bloccati in editazione")
        else:
            self.message_label.configure(text="Username o Password errati!",  text_color="red",font=("Roboto", 15, "bold"))

    # Apertura label con informazioni versione e autore
    def open_info(self):
        print("Info")
        log("INFO", "Apertura finestra di informazioni del software")
        self.info_window = ctk.CTkToplevel()
        self.info_window.grab_set()
        self.info_window.title("Informazioni sul software")
        self.info_window.resizable(False, False)

        # Centraggio della finestra di info
        self.center_win_detail(self.info_window, 350, 210)

        # ---------------- Grafica della finestra ---------------- 
        frame_info = ctk.CTkFrame(self.info_window, corner_radius=4)
        frame_info.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # info
        label_info = ctk.CTkLabel(frame_info, 
                                  text="Software sviluppato per l'archiviazione tecnica", 
                                  font=("Roboto", 15)
                                  )
        label_info.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsw")

        # versione
        label_version = ctk.CTkLabel(frame_info, text="Versione:", font=("Roboto", 15, "bold"))
        label_version.grid(row=1, column=0, padx=10, pady=10, sticky="nsw")
        label_version_number = ctk.CTkLabel(frame_info, text="v0.0", font=("Roboto", 15))
        label_version_number.grid(row=1, column=1, padx=10, pady=10, sticky="nsw")

        # autore
        label_autor = ctk.CTkLabel(frame_info, text="Autori:", font=("Roboto", 15, "bold"))
        label_autor.grid(row=2, column=0, padx=10, pady=10, sticky="nsw")
        label_autor_name = ctk.CTkLabel(frame_info, text="Merola Riccardo, Martini Enrico", font=("Roboto", 15))
        label_autor_name.grid(row=2, column=1, padx=10, pady=10, sticky="nsw")

        # pulsante ok
        button_ok = ctk.CTkButton(frame_info, text="Ok", font=("Roboto", 13), command=self.info_window.destroy)
        button_ok.grid(row=3, column=1, padx=10, pady=10, sticky="nse")

    # Funzione per segnalazione di problemi o bug
    def signal_problem(self):
        try:
            # collegamento all'applicazione outlook installata
            outlook = win32.Dispatch('outlook.application')
            # creazione della mail (0 indica oggetto di tipo "mail")
            mail = outlook.CreateItem(0)

            mail.To = "Merola.Riccardo@breton.it"
            mail.CC = "Martini.Enrico@breton.it"
            mail.Subject = "Archivio Errori: Segnalazione di problema o bug"
            # mostra la finestra di outlook all'utente senza inviare la mail
            log("INFO", "Apertura finestra di Outlook per segnalazione problemi")
            mail.Display(True)
        except Exception as err:
            log("ERROR", f"Apertura Outlook fallita: {err}")
            print(f"Impossibile aprire Outlook. Assicurarsi che sia installato: {err}")
            self.master.debug_message(f"Impossibile aprire Outlook. Assicurarsi che sia installato: {err}")

    # Funzione per centrare la finestra di dettaglio all'apertura
    def center_win_detail(self, window, width, height):
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        scale = window._get_window_scaling()

        x = int(((screen_width / 2) - (width / 2)) * scale)
        y = int(((screen_height / 2) - (height / 2)) * scale)
        window.geometry(f"{width}x{height}+{x}+{y}")