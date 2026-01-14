import sqlite3, os, base64, json
from datetime import datetime

# استدعاء مكتبة التشفير بشكل آمن لدعم NixOS
try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.fernet import Fernet
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

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
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    tag TEXT DEFAULT 'memo',
                    is_encrypted INTEGER DEFAULT 0,
                    created_at TEXT
                )
            """)

    def _get_key(self, password: str):
        salt = b'numrun_nixos_v010_salt'
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    # --- Commands Logic ---
    def add_command(self, command, alias=None, group='general'):
        with self.conn:
            self.conn.execute("INSERT INTO commands (command, alias, group_name) VALUES (?, ?, ?)", (command, alias, group))

    def get_all_commands(self):
        return self.conn.execute("SELECT cmd_number, command, group_name, usage_count, last_used, alias FROM commands ORDER BY cmd_number").fetchall()

    def get_by_group(self, group_name):
        return self.conn.execute("SELECT command, cmd_number FROM commands WHERE group_name = ?", (group_name,)).fetchall()

    def increment_usage(self, num):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.conn: self.conn.execute("UPDATE commands SET usage_count = usage_count + 1, last_used = ? WHERE cmd_number = ?", (now, num))

    # --- Notes Logic ---
    def add_note(self, title, content, password=None):
        if password and not HAS_CRYPTO: raise ImportError("cryptography module missing")
        is_enc = 0
        if password:
            f = Fernet(self._get_key(password))
            content = f.encrypt(content.encode()).decode()
            is_enc = 1
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.conn:
            self.conn.execute("INSERT INTO notes (title, content, is_encrypted, created_at) VALUES (?, ?, ?, ?)", (title, content, is_enc, now))

    def get_note(self, nid, password=None):
        res = self.conn.execute("SELECT title, content, is_encrypted, created_at FROM notes WHERE note_id = ?", (nid,)).fetchone()
        if not res: return None, None, None
        title, content, is_enc, date = res
        if is_enc:
            if not password: return "LOCKED", title, date
            try:
                f = Fernet(self._get_key(password))
                content = f.decrypt(content.encode()).decode()
            except: return "WRONG_PASS", title, date
        return content, title, date

    def get_all_notes(self):
        return self.conn.execute("SELECT note_id, title, is_encrypted, created_at FROM notes ORDER BY note_id DESC").fetchall()

    # --- Backup Logic ---
    def get_backup_data(self):
        cmds = self.conn.execute("SELECT * FROM commands").fetchall()
        notes = self.conn.execute("SELECT * FROM notes").fetchall()
        return {"commands": cmds, "notes": notes}

    def delete_cmd(self, num):
        with self.conn: self.conn.execute("DELETE FROM commands WHERE cmd_number = ?", (num,))
