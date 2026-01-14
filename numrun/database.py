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
                    group_name TEXT DEFAULT 'general',
                    usage_count INTEGER DEFAULT 0,
                    last_used TEXT,
                    alias TEXT UNIQUE
                )
            """)
            # التحقق من تحديث الأعمدة في النسخ القديمة
            cursor = self.conn.execute("PRAGMA table_info(commands)")
            cols = [c[1] for c in cursor.fetchall()]
            if 'group_name' not in cols: 
                self.conn.execute("ALTER TABLE commands ADD COLUMN group_name TEXT DEFAULT 'general'")
            if 'alias' not in cols: 
                self.conn.execute("ALTER TABLE commands ADD COLUMN alias TEXT")

    def add_command(self, command, alias=None, group='general'):
        with self.conn:
            cursor = self.conn.execute(
                "INSERT INTO commands (command, alias, group_name) VALUES (?, ?, ?)", 
                (command, alias, group)
            )
            return cursor.lastrowid

    def update_command(self, num, new_cmd, new_alias):
        with self.conn:
            self.conn.execute("UPDATE commands SET command = ?, alias = ? WHERE cmd_number = ?", 
                             (new_cmd, new_alias, num))

    def is_alias_exists(self, alias):
        if not alias: return False
        return self.conn.execute("SELECT 1 FROM commands WHERE alias = ?", (alias,)).fetchone() is not None

    def get_all(self, group=None):
        # تحديد الأعمدة بالاسم لضمان الترتيب الصحيح في الـ CLI
        query = "SELECT cmd_number, command, group_name, usage_count, last_used, alias FROM commands"
        if group:
            return self.conn.execute(query + " WHERE group_name = ?", (group,)).fetchall()
        return self.conn.execute(query + " ORDER BY cmd_number").fetchall()

    def get_by_id_or_alias(self, identifier):
        res = self.conn.execute("SELECT command, cmd_number, alias FROM commands WHERE alias = ?", (identifier,)).fetchone()
        if not res and str(identifier).isdigit():
            res = self.conn.execute("SELECT command, cmd_number, alias FROM commands WHERE cmd_number = ?", (identifier,)).fetchone()
        return res

    def increment_usage(self, num):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.conn:
            self.conn.execute("UPDATE commands SET usage_count = usage_count + 1, last_used = ? WHERE cmd_number = ?", (now, num))

    def delete(self, num):
        with self.conn: 
            self.conn.execute("DELETE FROM commands WHERE cmd_number = ?", (num,))
