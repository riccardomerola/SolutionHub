import sqlite3
import os

def get_connection():
    folder = "DB"

    if not os.path.exists(folder):
        os.makedirs(folder)

    db_path = os.path.join(folder, "archivio_errori.db")

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    connection = get_connection()
    cursor = connection.cursor()

    query = """
    CREATE TABLE IF NOT EXISTS archivio_errori(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
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

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_componente ON archivio_errori(Componente COLLATE NOCASE);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_problema ON archivio_errori(Problema COLLATE NOCASE);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_soluzione ON archivio_errori(Soluzione COLLATE NOCASE);")

    connection.commit()
    connection.close()