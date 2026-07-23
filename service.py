import repository as rep
import db
import logger as log
import os
from datetime import datetime
import shutil

class Service():
    def __init__(self):
        pass

    # Funzione per inizializzare db e creare il backup
    def initialize_database(self):
        db_integrity = rep.check_db_integrity()
        if db_integrity == "ok":
            log.log("INFO", "Integrità database: OK")
            db_path = r"Database\breton_solutionhub.db"
            bck_folder = r"Database\backup"

            # creazione cartella di backup
            if not os.path.exists(bck_folder):
                os.makedirs(bck_folder)

            # creazione nome del backup
            bck_name = f"backup_{datetime.now().strftime('%Y_%m_%d')}.db"
            bck_path = os.path.join(bck_folder, bck_name)

            # inserimento del backup nella cartella
            if not os.path.exists(bck_path):
                try:
                    shutil.copy2(db_path, bck_path)
                    log.log("INFO", f"Creato backup del database '{bck_name}'")
                except Exception as err:
                    log.log("ERROR", str(err))
                    return False
            db.create_table()
            return True
        else:
            log.log("CRITICAL", f"Errore di integrità del database - ERR: {db_integrity}")
            return False


    # Funzione per estrarre tutte le righe del database
    def get_database(self):
        raw_rows = rep.get_database()
        return raw_rows


    # Funzione per estrarre solo una riga del database
    def get_row(self, id):
        row = rep.get_dettaglio(id)
        return row


    # Funzione per la ricerca del solo testo
    def search(self, text):
        results = rep.search(text)
        return results


    # Funzione per la ricerca combinata di testo e filtro
    def search_with_filter(self, text, filter):
        result = rep.search_with_filter(text, filter)
        return result


    # Funzione per la ricerca con solo filtro
    def search_only_filter(self, filter):
        result = rep.search_only_filter(filter)
        return result


   # Funzione per eliminare un record dal database
    def delete_record(self, id):
        delete = rep.delete_record(id)
        return delete