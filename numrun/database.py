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
                    last_used TEXT,
                    alias TEXT UNIQUE
                )
            """)
            cursor = self.conn.execute("PRAGMA table_info(commands)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'last_used' not in columns:
                self.conn.execute("ALTER TABLE commands ADD COLUMN last_used TEXT")
            if 'alias' not in columns:
                self.conn.execute("ALTER TABLE commands ADD COLUMN alias TEXT")

    def add_command(self, command, alias_name=None):
        with self.conn:
            cursor = self.conn.execute(
                "INSERT INTO commands (command, alias) VALUES (?, ?)", 
                (command, alias_name)
            )
            return cursor.lastrowid

    def is_alias_exists(self, alias_name):
        if not alias_name: return False
        res = self.conn.execute("SELECT 1 FROM commands WHERE alias = ?", (alias_name,)).fetchone()
        return res is not None

    def get_all(self):
        return self.conn.execute("SELECT cmd_number, command, alias, usage_count, last_used FROM commands ORDER BY cmd_number").fetchall()

    def get_by_num(self, num):
        return self.conn.execute("SELECT command FROM commands WHERE cmd_number = ?", (num,)).fetchone()

    def get_by_alias(self, alias_name):
        return self.conn.execute("SELECT command, cmd_number FROM commands WHERE alias = ?", (alias_name,)).fetchone()

    def increment_usage(self, num):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.conn:
            self.conn.execute("UPDATE commands SET usage_count = usage_count + 1, last_used = ? WHERE cmd_number = ?", (now, num))

    def delete(self, num):
        with self.conn:
            self.conn.execute("DELETE FROM commands WHERE cmd_number = ?", (num,))

    def set_alias(self, num, alias_name):
        with self.conn:
            try:
                self.conn.execute("UPDATE commands SET alias = ? WHERE cmd_number = ?", (alias_name, num))
                return True
            except sqlite3.IntegrityError:
                return False
