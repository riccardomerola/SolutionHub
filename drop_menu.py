# qui si inseriranno le azioni della barra del menu (File, Help, ?) e poi verranno richiamate singolarmente attraveso il comando del singolo pulsante nella classe principale
# poi all'inizio della classe principale basterà inserire qualcosa tipo (supponendo di creare in questo file la classe MenuActions()): self.azioni = MenuActions(self)
# e poi ai pulsanti collegare il comando tipo (supponendo che nuova_azione sia un metodo della nuova vlasse): command = self.azioni.nuova_azione

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

# Classe della barra di menu
class MenuBar():
    def __init__(self):
        super().__init__()

    def change_database(self):
        print("Cambio database")

    def change_theme(self):
        print("Cambio tema")

    def open_instruction(self):
        print("Apertura istruzioni")

    def open_debug(self):
        print("Apertura debug")

    def open_info(self):
        print("Info")
        info_window = ctk.CTkToplevel()
        info_window.grab_set()
        info_window.title("Informazioni sul software")
        info_window.resizable(False, False)

        # Centraggio della finestra di info
        info_window.update_idletasks()
        screen_width = info_window.winfo_screenwidth()
        screen_height = info_window.winfo_screenheight()
        scale = info_window._get_window_scaling()
        x = int(((screen_width / 2) - (350 / 2)) * scale)
        y = int(((screen_height / 2) - (210 / 2)) * scale)
        info_window.geometry(f"350x210+{x}+{y}")

        # ---------------- Grafica della finestra ---------------- 
        frame_info = ctk.CTkFrame(info_window, corner_radius=4)
        frame_info.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # info
        label_info = ctk.CTkLabel(frame_info, text="Software sviluppato per l'archiviazione tecnica", font=("Roboto", 15))
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
        button_ok = ctk.CTkButton(frame_info, text="Ok", font=("Roboto", 13), command=info_window.destroy)
        button_ok.grid(row=3, column=1, padx=10, pady=10, sticky="nse")