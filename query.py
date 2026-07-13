from db import get_connection

# Controllo integrità del database
def check_db_integrity():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()[0]   # primo risultato della riga
        return result


# Visualizza tutto il contenuto del db
def get_database():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM breton_solutionhub")
        result = cursor.fetchall()
        return [dict(row) for row in result]


# Visualizza dettaglio del problema
def get_dettaglio(id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM breton_solutionhub WHERE id=?;", (id, ))
        result = cursor.fetchall()
        return [dict(row) for row in result]


# Ricerca di componente/problema/soluzione
def search(text):
    with get_connection() as conn:
        cursor = conn.cursor()

        query = """
        SELECT * FROM breton_solutionhub
        WHERE Elemento LIKE ? OR Problema LIKE ? OR Soluzione LIKE ?;"""

        cursor.execute(query, (f"%{text}%", f"%{text}%", f"%{text}%"))
        result = cursor.fetchall()
        return [dict(row) for row in result]


# Cancella un record
def delete_record(id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM breton_solutionhub WHERE id=?;", (id, ))
        conn.commit()
        result = cursor.fetchall()
        return [dict(row) for row in result]


# Ricava il record con ID maggiore
def get_max_id():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM breton_solutionhub ORDER BY ID DESC LIMIT 1;")
        result = cursor.fetchall()
        return [dict(row) for row in result]


# Inserisci record nel database
def insert_record(id, settore, elemento, problema, soluzione, documento, percorso, editazione, user, data):
    with get_connection() as conn:
        cursor = conn.cursor()

        query = "INSERT INTO breton_solutionhub VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"

        cursor.execute(query, (id, settore, elemento, problema, soluzione, documento, percorso, editazione, user, data))
        conn.commit()
        result = cursor.fetchall()
        return [dict(row) for row in result]


# Modifica un record già presente nel database
def edit_record(id, settore, elemento, problema, soluzione, documento, percorso, editazione, user, data):
    with get_connection() as conn:
        cursor = conn.cursor()

        query = """
        UPDATE breton_solutionhub
        SET Settore=?, Elemento=?, Problema=?, Soluzione=?, Documentazione=?, Percorso=?, Editazione=?, User=?, Data=?
        WHERE ID=?;
        """

        cursor.execute(query, (settore, elemento, problema, soluzione, documento, percorso, editazione, user, data, id))
        result = cursor.fetchall()
        return [dict(row) for row in result]


# Impostazione campo Editazione = 1
def set_editing(id):
    with get_connection() as conn:
        cursor = conn.cursor()

        query = """
        UPDATE breton_solutionhub SET Editazione=1 WHERE ID=?;
        """

        cursor.execute(query, (id, ))
        result = cursor.fetchall()
        return [dict(row) for row in result]

# Impostazione campo Editazione = 0 (chiusura editazione)
def close_editing(id):
    with get_connection() as conn:
        cursor = conn.cursor()

        query = """
        UPDATE breton_solutionhub SET Editazione=0 WHERE ID=?;
        """

        cursor.execute(query, (id, ))
        result = cursor.fetchall()
        return [dict(row) for row in result]


# Recupero dell'ID del record in editazione
def get_id_editing_record():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ID FROM breton_solutionhub WHERE Editazione=1;")
        result = cursor.fetchall()
        return [dict(row) for row in result]


# Reset dei record in editazione, da usare in caso di chiusure forzate del programma
def reset_editazione():
    with get_connection() as conn:
        cursor = conn.cursor()
        query= """
        UPDATE breton_solutionhub SET Editazione=0 WHERE Editazione=1;
        """
        cursor.execute(query, )
        result = cursor.fetchall()
        return [dict(row) for row in result]