import sqlite3
import os

def get_connection():
    folder = "Database"

    # creazione cartella e file db
    if not os.path.exists(folder):
        os.makedirs(folder)

    db_path = os.path.join(folder, "breton_solutionhub.db")

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    connection = get_connection()
    cursor = connection.cursor()

    query = """
    CREATE TABLE IF NOT EXISTS breton_solutionhub(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Macchina TEXT NOT NULL,
    Componente TEXT NOT NULL,
    Problema TEXT NOT NULL,
    Soluzione TEXT NOT NULL,
    Documentazione TEXT,
    Percorso TEXT DEFAULT NULL,
    Editazione INTEGER DEFAULT 0,
    User TEXT NOT NULL,
    Data TEXT NOT NULL);
    """
    cursor.execute(query)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_componente ON breton_solutionhub(Componente COLLATE NOCASE);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_problema ON breton_solutionhub(Problema COLLATE NOCASE);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_soluzione ON breton_solutionhub(Soluzione COLLATE NOCASE);")

    connection.commit()
    connection.close()