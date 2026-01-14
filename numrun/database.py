import sqlite3, os
from datetime import datetime

class Database:
    def __init__(self, db_path="~/.numrun.db"):
        self.db_path = os.path.expanduser(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # الوصول للبيانات بأسماء الأعمدة
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.executescript("""
                CREATE TABLE IF NOT EXISTS commands (
                    cmd_number INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    group_name TEXT DEFAULT 'general',
                    usage_count INTEGER DEFAULT 0,
                    last_used TEXT,
                    alias TEXT UNIQUE
                );
                CREATE TABLE IF NOT EXISTS notes (
                    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    tag TEXT DEFAULT 'memo',
                    created_at TEXT
                );
            """)

    def add_command(self, command, alias=None, group='general'):
        try:
            with self.conn:
                self.conn.execute("INSERT INTO commands (command, alias, group_name) VALUES (?, ?, ?)", (command, alias, group))
            return True
        except sqlite3.IntegrityError: return False

    def update_command(self, cmd_id, new_cmd):
        with self.conn:
            self.conn.execute("UPDATE commands SET command = ? WHERE cmd_number = ?", (new_cmd, cmd_id))

    def update_alias(self, cmd_id, new_alias):
        try:
            with self.conn:
                self.conn.execute("UPDATE commands SET alias = ? WHERE cmd_number = ?", (new_alias, cmd_id))
            return True
        except sqlite3.IntegrityError: return False

    def get_all_commands(self):
        return self.conn.execute("SELECT * FROM commands ORDER BY cmd_number").fetchall()

    def get_by_group(self, group_name):
        return self.conn.execute("SELECT * FROM commands WHERE group_name = ?", (group_name,)).fetchall()

    def increment_usage(self, num):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.conn: 
            self.conn.execute("UPDATE commands SET usage_count = usage_count + 1, last_used = ? WHERE cmd_number = ?", (now, num))

    def delete_cmd(self, num):
        with self.conn:
            cursor = self.conn.execute("DELETE FROM commands WHERE cmd_number = ?", (num,))
            return cursor.rowcount > 0

    def add_note(self, title, content):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.conn:
            self.conn.execute("INSERT INTO notes (title, content, created_at) VALUES (?, ?, ?)", (title, content, now))

    def get_all_notes(self):
        return self.conn.execute("SELECT note_id, title, created_at FROM notes ORDER BY note_id DESC").fetchall()

    def get_note(self, nid):
        return self.conn.execute("SELECT * FROM notes WHERE note_id = ?", (nid,)).fetchone()

    def get_backup_data(self):
        cmds = [dict(row) for row in self.conn.execute("SELECT * FROM commands").fetchall()]
        notes = [dict(row) for row in self.conn.execute("SELECT * FROM notes").fetchall()]
        return {"commands": cmds, "notes": notes}
