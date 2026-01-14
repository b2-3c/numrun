import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_path="~/.numrun.db"):
        self.db_path = os.path.expanduser(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS commands (
                    cmd_number INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    tags TEXT,
                    usage_count INTEGER DEFAULT 0,
                    last_used TEXT
                )
            """)

    def add_command(self, command, num=None):
        with self.conn:
            if num:
                self.conn.execute("INSERT OR REPLACE INTO commands (cmd_number, command) VALUES (?, ?)", (num, command))
                return num
            else:
                cursor = self.conn.execute("INSERT INTO commands (command) VALUES (?)", (command,))
                return cursor.lastrowid

    def get_all(self):
        return self.conn.execute("SELECT * FROM commands ORDER BY cmd_number").fetchall()

    def get_by_num(self, num):
        res = self.conn.execute("SELECT command FROM commands WHERE cmd_number = ?", (num,)).fetchone()
        return res

    def increment_usage(self, num):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.conn:
            self.conn.execute("UPDATE commands SET usage_count = usage_count + 1, last_used = ? WHERE cmd_number = ?", (now, num))

    def update_command(self, num, new_cmd):
        with self.conn:
            self.conn.execute("UPDATE commands SET command = ? WHERE cmd_number = ?", (new_cmd, num))

    def add_tag(self, num, tag):
        with self.conn:
            res = self.conn.execute("SELECT tags FROM commands WHERE cmd_number = ?", (num,)).fetchone()
            current = res[0] if res and res[0] else ""
            tags = set(current.split(",")) if current else set()
            tags.add(tag)
            self.conn.execute("UPDATE commands SET tags = ? WHERE cmd_number = ?", (",".join(filter(None, tags)), num))

    def delete(self, num):
        with self.conn:
            self.conn.execute("DELETE FROM commands WHERE cmd_number = ?", (num,))

    def search(self, query):
        q = f"%{query}%"
        return self.conn.execute("SELECT * FROM commands WHERE command LIKE ? OR tags LIKE ?", (q, q)).fetchall()
