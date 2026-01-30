import sqlite3, os
from datetime import datetime

class Database:
    def __init__(self, db_path="~/.numrun.db"):
        self.db_path = os.path.expanduser(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row 
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.executescript("""
                CREATE TABLE IF NOT EXISTS commands (
                    cmd_number INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    alias TEXT UNIQUE,
                    created_at TEXT,
                    last_used TEXT
                );
                CREATE TABLE IF NOT EXISTS notes (
                    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    created_at TEXT,
                    updated_at TEXT
                );
            """)

    def add_command(self, command, alias=None):
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            with self.conn:
                self.conn.execute(
                    "INSERT INTO commands (command, alias, created_at, usage_count) VALUES (?, ?, ?, ?)", 
                    (command, alias, now, 0)
                )
            return True
        except sqlite3.IntegrityError: 
            return False

    def get_all_commands(self):
        return self.conn.execute("SELECT * FROM commands ORDER BY cmd_number").fetchall()

    def get_commands_by_usage(self):
        """الحصول على الأوامر مرتبة حسب الاستخدام (الأكثر استخداماً أولاً)"""
        return self.conn.execute("SELECT * FROM commands ORDER BY usage_count DESC, cmd_number").fetchall()

    def increment_usage(self, cmd_id):
        """زيادة عدد مرات استخدام الأمر"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.conn:
            self.conn.execute(
                "UPDATE commands SET usage_count = usage_count + 1, last_used = ? WHERE cmd_number = ?", 
                (now, cmd_id)
            )

    def add_note(self, title, content):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.conn:
            self.conn.execute(
                "INSERT INTO notes (title, content, created_at, updated_at) VALUES (?, ?, ?, ?)", 
                (title, content, now, now)
            )

    def get_all_notes(self):
        return self.conn.execute("SELECT note_id, title, created_at, updated_at FROM notes ORDER BY note_id DESC").fetchall()

    def get_note(self, nid):
        return self.conn.execute("SELECT * FROM notes WHERE note_id = ?", (nid,)).fetchone()

    def update_command(self, cmd_id, new_cmd=None, new_alias=None):
        with self.conn:
            if new_cmd: 
                self.conn.execute("UPDATE commands SET command = ? WHERE cmd_number = ?", (new_cmd, cmd_id))
            if new_alias:
                try: 
                    self.conn.execute("UPDATE commands SET alias = ? WHERE cmd_number = ?", (new_alias, cmd_id))
                except sqlite3.IntegrityError: 
                    return False
        return True

    def update_note(self, note_id, new_title=None, new_content=None):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.conn:
            if new_title: 
                self.conn.execute("UPDATE notes SET title = ?, updated_at = ? WHERE note_id = ?", (new_title, now, note_id))
            if new_content: 
                self.conn.execute("UPDATE notes SET content = ?, updated_at = ? WHERE note_id = ?", (new_content, now, note_id))
        return True

    def delete_cmd(self, num):
        with self.conn:
            return self.conn.execute("DELETE FROM commands WHERE cmd_number = ?", (num,)).rowcount > 0

    def delete_note(self, nid):
        with self.conn:
            return self.conn.execute("DELETE FROM notes WHERE note_id = ?", (nid,)).rowcount > 0

    def get_stats(self):
        cmd_count = self.conn.execute("SELECT COUNT(*) FROM commands").fetchone()[0]
        note_count = self.conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
        total_usage = self.conn.execute("SELECT SUM(usage_count) FROM commands").fetchone()[0] or 0
        return cmd_count, note_count, total_usage

    def get_command_by_id_or_alias(self, identifier):
        """الحصول على أمر باستخدام المعرف أو الاسم المستعار"""
        return self.conn.execute(
            "SELECT * FROM commands WHERE cmd_number = ? OR alias = ?", 
            (identifier, identifier)
        ).fetchone()
