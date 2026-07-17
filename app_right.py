from CTkToolTip import CTkToolTip
import customtkinter as ctk
from tkinter import ttk
import query
import os
from logger import log
from datetime import datetime
from expand_text import LargeTextEditor
from CTkMessagebox import CTkMessagebox

# Classe per la parte destra della finestra principale
class RightPanel(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master)
        self.app = app
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Barra di ricerca e combobox filtri
        self.search_entry = ctk.CTkEntry(
            master=self.app.right_frame,
            placeholder_text="🔎 Cerca",
            height=40,
            corner_radius=4,
            font=("Roboto", 18)
        )
        self.search_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        #self.search_entry.bind("<KeyRelease>", self.dynamic_search)

        self.filter_combobox = ctk.CTkComboBox(
            master=self.app.right_frame,
            height=40,
            width=300,
            values=["Nessun filtro di ricerca", "Altro", "Fabshop", "Meccanica", "Levigatrici", "Impianti", "Ricambi"],
            state="readonly",
            font=("Roboto", 18),
            dropdown_font=("Roboto", 15),
            command=None#self.load_data
        )
        self.filter_combobox.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="e")
        self.filter_combobox.set("Nessun filtro di ricerca")

        # Eventi per evidenziare la combobox
        self.search_entry.bind("<Enter>", self.on_hover)
        self.search_entry.bind("<Leave>", self.on_leave)

        # =================== TABELLA TREEVIEV ===================
        self.table_frame = ctk.CTkFrame(master=self.app.right_frame, corner_radius=4)
        self.table_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.table_frame.grid_columnconfigure((0, 1), weight=1)
        self.table_frame.grid_rowconfigure((0, 1), weight=1)

        # Stile ttk, scrollbar
        self.style = ttk.Style()
        self.style.theme_use("winnative")
        self.scrollbar_y = ctk.CTkScrollbar(master=self.table_frame, orientation="vertical")

        # Stile della heading e delle celle della tabella
        self.style.configure(
            "Treeview.Heading",
            background=self.app.theme["BG_COLOR_HEADING"],
            foreground=self.app.theme["FG_COLOR"],
            borderwidth=1,
            relief="solid",
            padding=(0, 8, 0, 8),
            font=("Roboto", 15, "bold")
        )
        self.style.configure(
            "Treeview",
            background=self.app.theme["BG_COLOR_TREEVIEW"],
            foreground=self.app.theme["FG_COLOR"],
            fieldbackground=self.app.theme["BG_COLOR_TREEVIEW"],
            rowheight=40,
            borderwidth=1,
            relief="flat",
            font=("Roboto", 11)
        )
        self.style.map("Treeview", background=[("selected", "#3b8ed0")])

        # Creazione della tabella
        self.value_table = ttk.Treeview(
            master=self.table_frame,
            columns=("id", "sector", "object", "problem", "solution", "doc"),
            show="headings",
            yscrollcommand=self.scrollbar_y.set
        )
        CTkToolTip(
            self.value_table,
            message="Doppio click sul record per aprire il dettaglio",
            corner_radius=8,
            border_width=1,
            border_color="white"
        )
        # Heading delle colonne
        self.value_table.heading("id", text="ID")
        self.value_table.heading("sector", text="Settore")
        self.value_table.heading("object", text="Oggetto")
        self.value_table.heading("problem", text="Problema")
        self.value_table.heading("solution", text="Soluzione")
        self.value_table.heading("doc", text="Allegato")

        # Impostazione delle colonne
        self.value_table.column("id", width=15, stretch=True, anchor="center")
        self.value_table.column("sector", width=90, stretch=True, anchor="center")
        self.value_table.column("object", width=100, stretch=True, anchor="center")
        self.value_table.column("problem", width=400, stretch=True, anchor="w")
        self.value_table.column("solution", width=400, stretch=True, anchor="w")
        self.value_table.column("doc", width=80, stretch=True, anchor="center")

        # Definizione dei tag per le righe della tabelle
        self.value_table.tag_configure("pari", background=self.app.theme["BG_COLOR_TREEVIEW"])
        self.value_table.tag_configure("dispari", background=self.app.theme["BG_COLOR_TREEVIEW_ALTERNATE"])
        self.value_table.tag_configure("nessun_risultato", foreground="orange")

        # Posizionamento della tabella e della scrollbar
        self.scrollbar_y.configure(command=self.value_table.yview)
        self.scrollbar_y.pack(side="right", fill="y")
        self.value_table.pack(padx=0, pady=0, fill="both", expand=True)

        # Eventi per la gestione dei click sulla tabella
        self.value_table.bind("<<TreeviewSelect>>", self.handle_table_click)
        self.value_table.bind("<Double-1>", self.handle_double_click)

        # Pulsante per visualizzare il dettaglio del record selezionato
        self.open_detail = ctk.CTkButton(
            master=self.app.right_frame,
            text="Apri dettaglio del record selezionato ℹ️",
            font=("Roboto", 15),
            command=None#self.handle_double_click
        )
        self.open_detail.grid(column=0, row=2, columnspan=2, padx=10, pady=10, sticky="ew")

        # ======================= FINE INIZIALIZZAZIONE DEL FRAME =======================