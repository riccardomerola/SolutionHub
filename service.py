import repository as rep
import db
import logger as log
import os
from datetime import datetime
import shutil

class Service():
    def __init__(self):
        pass

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