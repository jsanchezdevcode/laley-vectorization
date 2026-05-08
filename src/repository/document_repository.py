import sqlite3

class DocumentRepository:

    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_all_document_ids(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM document_index")
        rows = cursor.fetchall()

        conn.close()

        return [r[0] for r in rows]