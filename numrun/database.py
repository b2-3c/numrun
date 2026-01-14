import sqlite3, os, json
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
            # جدول المذكرات (بدون تشفير)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    tag TEXT DEFAULT 'memo',
                    created_at TEXT
                )
            """)

    # --- منطق الأوامر ---
    def add_command(self, command, alias=None, group='general'):
        with self.conn:
            self.conn.execute("INSERT INTO commands (command, alias, group_name) VALUES (?, ?, ?)", 
                              (command, alias, group))

    def get_all_commands(self):
        return self.conn.execute("SELECT cmd_number, command, group_name, usage_count, last_used, alias FROM commands ORDER BY cmd_number").fetchall()

    def get_by_group(self, group_name):
        return self.conn.execute("SELECT command, cmd_number FROM commands WHERE group_name = ?", (group_name,)).fetchall()

    def increment_usage(self, num):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.conn: 
            self.conn.execute("UPDATE commands SET usage_count = usage_count + 1, last_used = ? WHERE cmd_number = ?", (now, num))

    def delete_cmd(self, num):
        with self.conn: self.conn.execute("DELETE FROM commands WHERE cmd_number = ?", (num,))

    # --- منطق المذكرات (نص بسيط) ---
    def add_note(self, title, content):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.conn:
            self.conn.execute("INSERT INTO notes (title, content, created_at) VALUES (?, ?, ?)", (title, content, now))

    def get_note(self, nid):
        return self.conn.execute("SELECT title, content, created_at FROM notes WHERE note_id = ?", (nid,)).fetchone()

    def get_all_notes(self):
        return self.conn.execute("SELECT note_id, title, created_at FROM notes ORDER BY note_id DESC").fetchall()

    # --- النسخ الاحتياطي ---
    def get_backup_data(self):
        cmds = self.conn.execute("SELECT * FROM commands").fetchall()
        notes = self.conn.execute("SELECT * FROM notes").fetchall()
        return {"commands": cmds, "notes": notes}
