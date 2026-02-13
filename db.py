import pymysql

class DB:
    def __init__(self):
        self.conn = pymysql.connect(
            host="localhost",
            user="root",
            password="changed",
            database="db10",   # <-- IMPORTANT: use the DB where your old tables exist
            autocommit=True
        )

    def run(self, query, params=None, fetch=False, fetchone=False):
        params = params or ()
        with self.conn.cursor() as cur:
            cur.execute(query, params)

            if fetchone:
                return cur.fetchone()
            if fetch:
                return cur.fetchall()

            # for INSERT/UPDATE/DELETE return True if query worked
            return True
