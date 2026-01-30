import sqlite3, os
from datetime import datetime

class Database:
    def __init__(self, db_path="~/.numrun.db"):
        self.db_path = os.path.expanduser(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row 
        self.create_table()
        self.migrate()

    def create_table(self):
        with self.conn:
            self.conn.executescript("""
                CREATE TABLE IF NOT EXISTS commands (
                    cmd_number INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    alias TEXT UNIQUE,
                    tags TEXT,
                    created_at TEXT,
                    last_used TEXT
                );
                CREATE TABLE IF NOT EXISTS notes (
                    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    tags TEXT,
                    created_at TEXT,
                    updated_at TEXT
                );
                CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT,
                    duration_minutes INTEGER,
                    task_name TEXT,
                    status TEXT
                );
            """)

    def migrate(self):
        """إضافة الأعمدة المفقودة تلقائياً في حال وجود قاعدة بيانات قديمة"""
        cursor = self.conn.cursor()
        
        # تحسين جدول commands
        cursor.execute("PRAGMA table_info(commands)")
        columns = [column[1] for column in cursor.fetchall()]
        
        with self.conn:
            if "tags" not in columns:
                self.conn.execute("ALTER TABLE commands ADD COLUMN tags TEXT")
            if "created_at" not in columns:
                self.conn.execute("ALTER TABLE commands ADD COLUMN created_at TEXT")
            if "last_used" not in columns:
                self.conn.execute("ALTER TABLE commands ADD COLUMN last_used TEXT")
            if "usage_count" not in columns:
                self.conn.execute("ALTER TABLE commands ADD COLUMN usage_count INTEGER DEFAULT 0")

        # تحسين جدول notes
        cursor.execute("PRAGMA table_info(notes)")
        columns = [column[1] for column in cursor.fetchall()]
        
        with self.conn:
            if "tags" not in columns:
                self.conn.execute("ALTER TABLE notes ADD COLUMN tags TEXT")
            if "updated_at" not in columns:
                self.conn.execute("ALTER TABLE notes ADD COLUMN updated_at TEXT")

    # --- Command Methods ---
    def add_command(self, command, alias=None, tags=""):
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            with self.conn:
                self.conn.execute(
                    "INSERT INTO commands (command, alias, tags, created_at, usage_count) VALUES (?, ?, ?, ?, ?)", 
                    (command, alias, tags, now, 0)
                )
            return True
        except sqlite3.IntegrityError: 
            return False

    def get_all_commands(self, sort_by="cmd_number"):
        if sort_by == "usage":
            return self.conn.execute("SELECT * FROM commands ORDER BY usage_count DESC, cmd_number").fetchall()
        return self.conn.execute("SELECT * FROM commands ORDER BY cmd_number").fetchall()

    def get_command_by_id_or_alias(self, identifier):
        return self.conn.execute(
            "SELECT * FROM commands WHERE cmd_number = ? OR alias = ?", 
            (identifier, identifier)
        ).fetchone()

    def increment_usage(self, cmd_id):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.conn:
            self.conn.execute(
                "UPDATE commands SET usage_count = usage_count + 1, last_used = ? WHERE cmd_number = ?", 
                (now, cmd_id)
            )

    def update_command(self, cmd_id, new_cmd=None, new_alias=None, new_tags=None):
        with self.conn:
            if new_cmd: 
                self.conn.execute("UPDATE commands SET command = ? WHERE cmd_number = ?", (new_cmd, cmd_id))
            if new_tags is not None:
                self.conn.execute("UPDATE commands SET tags = ? WHERE cmd_number = ?", (new_tags, cmd_id))
            if new_alias:
                try: 
                    self.conn.execute("UPDATE commands SET alias = ? WHERE cmd_number = ?", (new_alias, cmd_id))
                except sqlite3.IntegrityError: 
                    return False
        return True

    def delete_cmd(self, num):
        with self.conn:
            return self.conn.execute("DELETE FROM commands WHERE cmd_number = ? OR alias = ?", (num, num)).rowcount > 0

    # --- Note Methods ---
    def add_note(self, title, content, tags=""):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.conn:
            self.conn.execute(
                "INSERT INTO notes (title, content, tags, created_at, updated_at) VALUES (?, ?, ?, ?, ?)", 
                (title, content, tags, now, now)
            )

    def get_all_notes(self):
        return self.conn.execute("SELECT * FROM notes ORDER BY updated_at DESC").fetchall()

    def get_note(self, nid):
        return self.conn.execute("SELECT * FROM notes WHERE note_id = ?", (nid,)).fetchone()

    def update_note(self, note_id, new_title=None, new_content=None, new_tags=None):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.conn:
            if new_title: 
                self.conn.execute("UPDATE notes SET title = ?, updated_at = ? WHERE note_id = ?", (new_title, now, note_id))
            if new_content: 
                self.conn.execute("UPDATE notes SET content = ?, updated_at = ? WHERE note_id = ?", (new_content, now, note_id))
            if new_tags is not None:
                self.conn.execute("UPDATE notes SET tags = ?, updated_at = ? WHERE note_id = ?", (new_tags, now, note_id))
        return True

    def delete_note(self, nid):
        with self.conn:
            return self.conn.execute("DELETE FROM notes WHERE note_id = ?", (nid,)).rowcount > 0

    # --- Pomodoro Methods ---
    def log_pomodoro(self, task_name, duration, status="Completed"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.conn:
            self.conn.execute(
                "INSERT INTO pomodoro_sessions (start_time, duration_minutes, task_name, status) VALUES (?, ?, ?, ?)",
                (now, duration, task_name, status)
            )

    def get_pomodoro_stats(self):
        res = self.conn.execute(
            "SELECT COUNT(*), SUM(duration_minutes) FROM pomodoro_sessions WHERE status = 'Completed'"
        ).fetchone()
        count = res[0] or 0
        minutes = res[1] or 0
        return count, minutes

    # --- General ---
    def get_stats(self):
        cmd_count = self.conn.execute("SELECT COUNT(*) FROM commands").fetchone()[0]
        note_count = self.conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
        res_usage = self.conn.execute("SELECT SUM(usage_count) FROM commands").fetchone()
        total_usage = res_usage[0] if res_usage and res_usage[0] else 0
        return cmd_count, note_count, total_usage

    def export_data(self):
        cmds = [dict(r) for r in self.get_all_commands()]
        notes = [dict(r) for r in self.get_all_notes()]
        pomo = [dict(r) for r in self.conn.execute("SELECT * FROM pomodoro_sessions").fetchall()]
        return {"commands": cmds, "notes": notes, "pomodoro": pomo}
