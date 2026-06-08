from db import get_connection

# Visualizza tutto il contenuto del db
def get_database():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM archivio_errori")
        result = cursor.fetchall()
        return [dict(row) for row in result]
    

# Visualizza dettaglio del problema
def get_dettaglio(id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM archivio_errori WHERE id=?;", (id, ))
        result = cursor.fetchall()
        return [dict(row) for row in result]


# Ricerca di componente/problema/soluzione
def search(text):
    with get_connection() as conn:
        cursor = conn.cursor()
        
        query = """
        SELECT * FROM archivio_errori 
        WHERE Componente LIKE ? OR Problema LIKE ? OR Soluzione LIKE ?;"""
        
        cursor.execute(query, (f"%{text}%", f"%{text}%", f"%{text}%"))
        result = cursor.fetchall()
        return [dict(row) for row in result]
    

# Cancella un record
def delete_record(id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM archivio_errori WHERE id=?;", (id, ))
        conn.commit()
        result = cursor.fetchall()
        return [dict(row) for row in result]
    

# Ricava il record con ID maggiore
def get_max_id():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM archivio_errori ORDER BY ID DESC LIMIT 1;")
        result = cursor.fetchall()
        return [dict(row) for row in result]


# Inserisci record nel database
def insert_record(id, componente, problema, soluzione, documento, percorso, editazione, user, data):
    with get_connection() as conn:
        cursor = conn.cursor()

        query = "INSERT INTO archivio_errori VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"

        cursor.execute(query, (id, componente, problema, soluzione, documento, percorso, editazione, user, data))
        conn.commit()
        result = cursor.fetchall()
        return [dict(row) for row in result]
    

# Modifica un record già presente nel database
def edit_record(id, componente, problema, soluzione, documento, percorso, editazione, user, data):
    with get_connection() as conn:
        cursor = conn.cursor()

        query = """
        UPDATE archivio_errori
        SET Componente=?, Problema=?, Soluzione=?, Documentazione=?, Percorso=?, Editazione=?, User=?, Data=?
        WHERE ID=?;
        """

        cursor.execute(query, (componente, problema, soluzione, documento, percorso, editazione, user, data, id))
        result = cursor.fetchall()
        return [dict(row) for row in result]
    

# Impostazione campo Editazione = 1
def set_editing(id):
    with get_connection() as conn:
        cursor = conn.cursor()

        query = """
        UPDATE archivio_errori SET Editazione=1 WHERE ID=?;
        """

        cursor.execute(query, (id, ))
        result = cursor.fetchall()
        return [dict(row) for row in result]

# Impostazione campo Editazione = 0 (chiusura editazione)
def close_editing(id):
    with get_connection() as conn:
        cursor = conn.cursor()

        query = """
        UPDATE archivio_errori SET Editazione=0 WHERE ID=?;
        """

        cursor.execute(query, (id, ))
        result = cursor.fetchall()
        return [dict(row) for row in result]


# Recupero dell'ID del record in editazione
def get_id_editing_record():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ID FROM archivio_errori WHERE Editazione=1;")
        result = cursor.fetchall()
        return [dict(row) for row in result]