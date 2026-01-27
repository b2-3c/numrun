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
                    tags TEXT DEFAULT '',
                    is_fav INTEGER DEFAULT 0,
                    note_inline TEXT DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS notes (
                    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    created_at TEXT
                );
                CREATE TABLE IF NOT EXISTS variables (name TEXT PRIMARY KEY, value TEXT);
                CREATE TABLE IF NOT EXISTS templates (name TEXT PRIMARY KEY, content TEXT);
                CREATE TABLE IF NOT EXISTS pomodoro_log (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, type TEXT, duration INTEGER);
            """)

    def add_command(self, command, alias=None, tags="", note=""):
        try:
            with self.conn:
                self.conn.execute("INSERT INTO commands (command, alias, tags, note_inline) VALUES (?, ?, ?, ?)", 
                                 (command, alias, tags, note))
            return True
        except sqlite3.IntegrityError: return False

    def get_all_commands(self, fav_only=False):
        q = "SELECT * FROM commands"
        if fav_only: q += " WHERE is_fav = 1"
        return self.conn.execute(q + " ORDER BY is_fav DESC, usage_count DESC, cmd_number ASC").fetchall()

    def update_command(self, cmd_id, new_cmd=None, new_alias=None):
        with self.conn:
            if new_cmd: self.conn.execute("UPDATE commands SET command = ? WHERE cmd_number = ?", (new_cmd, cmd_id))
            if new_alias: self.conn.execute("UPDATE commands SET alias = ? WHERE cmd_number = ?", (new_alias, cmd_id))

    def toggle_fav(self, cid):
        with self.conn: self.conn.execute("UPDATE commands SET is_fav = 1 - is_fav WHERE cmd_number = ?", (cid,))

    def delete_cmd(self, num):
        with self.conn: return self.conn.execute("DELETE FROM commands WHERE cmd_number = ?", (num,)).rowcount > 0

    def add_note(self, title, content):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.conn: self.conn.execute("INSERT INTO notes (title, content, created_at) VALUES (?, ?, ?)", (title, content, now))

    def get_all_notes(self): return self.conn.execute("SELECT * FROM notes ORDER BY note_id DESC").fetchall()

    def set_var(self, n, v):
        with self.conn: self.conn.execute("INSERT OR REPLACE INTO variables VALUES (?, ?)", (n, v))
    
    def get_vars(self):
        return {r['name']: r['value'] for r in self.conn.execute("SELECT * FROM variables").fetchall()}

    def add_tpl(self, n, c):
        with self.conn: self.conn.execute("INSERT OR REPLACE INTO templates VALUES (?, ?)", (n, c))

    def get_tpl(self, n):
        res = self.conn.execute("SELECT content FROM templates WHERE name = ?", (n,)).fetchone()
        return res['content'] if res else None

    def log_pomodoro(self, d, t, dur):
        with self.conn: self.conn.execute("INSERT INTO pomodoro_log (date, type, duration) VALUES (?, ?, ?)", (d, t, dur))
