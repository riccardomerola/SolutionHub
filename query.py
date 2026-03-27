from db import get_connection

# Visualizza tutto il contenuto del db
def get_database():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM archivio_errori")
        result = cursor.fetchall()
        return [dict(row) for row in result]