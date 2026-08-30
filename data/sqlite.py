import sqlite3
import time
from pathlib import Path


class Database:
    def __init__(self):
        self.connection = sqlite3.connect(
            Path(__file__).resolve().parent.parent / "data" / "secrets" / "workers.db",
            check_same_thread=False,
        )

        self.cursor = self.connection.cursor()

        self.create_table()

    def get_connection(self):
        return self.connection

    def create_table(self):
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS workers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL,
                port INTEGER,
                host TEXT,
                token TEXT,
                hostname TEXT,
                state_hostname TEXT,
                last_seen INTEGER
            )
        """)
        self.connection.commit()

    def reset(self):
        self.cursor.execute("DELETE FROM workers")
        self.connection.commit()

        self.create_table()

        self.cursor.execute("SELECT * FROM workers")
        return self.cursor.fetchall()

    def select_worker_by_name(self, name):
        self.cursor.execute("SELECT * FROM workers WHERE name = ?", (name,))
        return self.cursor.fetchone()

    def add_worker(
        self, name, status, port, host, token, hostname, state_hostname, last_seen
    ):
        self.cursor.execute(
            "INSERT INTO workers (name, status, port, host, token, hostname, state_hostname, last_seen) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (name, status, port, host, token, hostname, state_hostname, last_seen),
        )
        self.connection.commit()

    def get_workers(self):
        self.cursor.execute("SELECT * FROM workers")
        return self.cursor.fetchall()

    def delete_worker(self, id):
        self.cursor.execute("DELETE FROM workers WHERE id = ?", (id,))
        self.connection.commit()

    def update_worker(
        self, id, name, status, port, host, token, hostname, state_hostname, last_seen
    ):
        self.cursor.execute(
            "UPDATE workers SET name = ?, status = ?, port = ?, host = ?, token = ?, hostname = ?, state_hostname = ?, last_seen = ? WHERE id = ?",
            (name, status, port, host, token, hostname, state_hostname, last_seen, id),
        )
        self.connection.commit()

    def update_worker_status(self, id, status, hostname, state_hostname, last_seen):
        self.cursor.execute(
            "UPDATE workers SET status = ?, hostname = ?, state_hostname = ?, last_seen = ? WHERE id = ?",
            (status, hostname, state_hostname, last_seen, id),
        )
        self.connection.commit()

    def get_worker(self, id):
        self.cursor.execute("SELECT * FROM workers WHERE id = ?", (id,))
        return self.cursor.fetchone()


if __name__ == "__main__":
    db = Database()
    connection = db.get_connection()
    cursor = connection.cursor()

    db.reset()
    db.add_worker(
        "worker1",
        "ONLINE",
        8000,
        "127.0.0.1",
        "abc",
        "localhost",
        "localhost",
        time.time(),
    )
    workers = db.get_workers()
    print(workers)
    db.update_worker_status(1, "OFFLINE", "localhost", "localhost", time.time())
    workers = db.get_workers()[0][8]
    print(workers)
