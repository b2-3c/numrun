import sqlite3, os
from datetime import datetime

class Database:
    def __init__(self, db_path="~/.numrun.db"):
        self.db_path = os.path.expanduser(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.create_table()

    def create_table(self):
        with self.conn:
            # جدول الأوامر
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
            # جدول المذكرات
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    tag TEXT DEFAULT 'memo',
                    created_at TEXT
                )
            """)
            # تحديث الأعمدة للنسخ القديمة
            cursor = self.conn.execute("PRAGMA table_info(commands)")
            cols = [c[1] for c in cursor.fetchall()]
            if 'group_name' not in cols: self.conn.execute("ALTER TABLE commands ADD COLUMN group_name TEXT DEFAULT 'general'")
            if 'alias' not in cols: self.conn.execute("ALTER TABLE commands ADD COLUMN alias TEXT")

    def add_command(self, command, alias=None, group='general'):
        with self.conn:
            cursor = self.conn.execute("INSERT INTO commands (command, alias, group_name) VALUES (?, ?, ?)", (command, alias, group))
            return cursor.lastrowid

    def get_all_commands(self):
        return self.conn.execute("SELECT cmd_number, command, group_name, usage_count, last_used, alias FROM commands ORDER BY cmd_number").fetchall()

    def get_by_group(self, group_name):
        return self.conn.execute("SELECT command, cmd_number FROM commands WHERE group_name = ? ORDER BY cmd_number", (group_name,)).fetchall()

    def get_by_id_or_alias(self, identifier):
        res = self.conn.execute("SELECT command, cmd_number, alias FROM commands WHERE alias = ?", (identifier,)).fetchone()
        if not res and str(identifier).isdigit():
            res = self.conn.execute("SELECT command, cmd_number, alias FROM commands WHERE cmd_number = ?", (identifier,)).fetchone()
        return res

    def delete_cmd(self, num):
        with self.conn: self.conn.execute("DELETE FROM commands WHERE cmd_number = ?", (num,))

    def increment_usage(self, num):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.conn: self.conn.execute("UPDATE commands SET usage_count = usage_count + 1, last_used = ? WHERE cmd_number = ?", (now, num))

    def add_note(self, title, content, tag='memo'):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.conn:
            cursor = self.conn.execute("INSERT INTO notes (title, content, tag, created_at) VALUES (?, ?, ?, ?)", (title, content, tag, now))
            return cursor.lastrowid

    def get_all_notes(self):
        return self.conn.execute("SELECT * FROM notes ORDER BY note_id DESC").fetchall()

    def get_note_by_id(self, nid):
        return self.conn.execute("SELECT title, content, tag, created_at FROM notes WHERE note_id = ?", (nid,)).fetchone()

    def delete_note(self, nid):
        with self.conn: self.conn.execute("DELETE FROM notes WHERE note_id = ?", (nid,))
