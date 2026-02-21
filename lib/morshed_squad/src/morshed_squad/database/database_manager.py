import sqlite3
import os
import hashlib
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="morshed.db", user_id=None):
        self.db_path = db_path
        self.user_id = user_id
        self._initialize_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _initialize_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Migration checks: Rename old tables that clash with new unique constraints
            cursor.execute("PRAGMA table_info(custom_agents)")
            cols = [col[1] for col in cursor.fetchall()]
            if cols and 'user_id' not in cols:
                try: cursor.execute("ALTER TABLE custom_agents RENAME TO custom_agents_v1_backup")
                except: pass
                try: cursor.execute("ALTER TABLE custom_tasks RENAME TO custom_tasks_v1_backup")
                except: pass
                try: cursor.execute("ALTER TABLE agent_memory RENAME TO agent_memory_v1_backup")
                except: pass

            # 2. Users Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password_hash TEXT,
                    api_key TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 3. Create Tenant-Isolated Tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    name TEXT,
                    phone TEXT,
                    email TEXT,
                    status TEXT DEFAULT 'Pending',
                    research_summary TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS telephony_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    lead_id INTEGER,
                    provider TEXT,
                    sid TEXT,
                    type TEXT,
                    result TEXT,
                    transcript TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_memory (
                    user_id INTEGER DEFAULT 1,
                    key TEXT,
                    value TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, key)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS social_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    platform TEXT,
                    topic TEXT,
                    content TEXT,
                    status TEXT DEFAULT 'Pending',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_outputs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    crew_name TEXT,
                    output TEXT,
                    status TEXT DEFAULT 'Success',
                    execution_time REAL,
                    metadata TEXT,
                    tokens_used INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS custom_agents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    name TEXT,
                    role TEXT,
                    goal TEXT,
                    backstory TEXT,
                    temperature REAL DEFAULT 0.7,
                    tools TEXT,
                    UNIQUE(user_id, name)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS custom_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    name TEXT,
                    description TEXT,
                    expected_output TEXT,
                    agent_name TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, name)
                )
            """)
            
            # Interceptor Table for Human-in-the-Loop
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pending_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    tool_name TEXT,
                    action_details TEXT,
                    status TEXT DEFAULT 'Pending',
                    feedback TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 4. Migrations - Adding user_id to remaining existing tables
            tables_to_migrate = ['leads', 'telephony_logs', 'social_posts', 'agent_outputs']
            for table in tables_to_migrate:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                if columns and 'user_id' not in columns:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN user_id INTEGER DEFAULT 1")
                    
            # 5. Detailed column migrations
            cursor.execute("PRAGMA table_info(agent_outputs)")
            columns = [col[1] for col in cursor.fetchall()]
            if columns:
                if 'status' not in columns: cursor.execute("ALTER TABLE agent_outputs ADD COLUMN status TEXT DEFAULT 'Success'")
                if 'execution_time' not in columns: cursor.execute("ALTER TABLE agent_outputs ADD COLUMN execution_time REAL")
                if 'metadata' not in columns: cursor.execute("ALTER TABLE agent_outputs ADD COLUMN metadata TEXT")
                if 'tokens_used' not in columns: cursor.execute("ALTER TABLE agent_outputs ADD COLUMN tokens_used INTEGER")
                
            cursor.execute("PRAGMA table_info(telephony_logs)")
            columns = [col[1] for col in cursor.fetchall()]
            if columns and 'transcript' not in columns:
                cursor.execute("ALTER TABLE telephony_logs ADD COLUMN transcript TEXT")

            # 6. Default Admin User setup for backward compatibility (Adopts old rows with user_id=1)
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                default_hash = hashlib.sha256(b"admin123").hexdigest()
                cursor.execute("INSERT INTO users (id, username, password_hash) VALUES (1, 'admin', ?)", (default_hash,))

            conn.commit()

    # --- User Management ---
    def create_user(self, username, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, password_hash)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
            
    def verify_user(self, username, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, password_hash))
            row = cursor.fetchone()
            return dict(row) if row else None
            
    def update_api_key(self, api_key):
        if not self.user_id: return
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET api_key = ? WHERE id = ?",
                (api_key, self.user_id)
            )
            conn.commit()
            
    def get_api_key(self):
        if not self.user_id: return None
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT api_key FROM users WHERE id = ?", (self.user_id,))
            row = cursor.fetchone()
            return row[0] if row else None

    # --- Data Operations (Tenant-Isolated) ---
    def add_lead(self, name, phone, email=None):
        if not self.user_id: return None
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO leads (user_id, name, phone, email) VALUES (?, ?, ?, ?)",
                    (self.user_id, name, phone, email)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def save_agent_memory(self, key, value):
        if not self.user_id: return
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO agent_memory (user_id, key, value, updated_at) VALUES (?, ?, ?, ?)",
                (self.user_id, key, value, datetime.now())
            )
            conn.commit()

    def save_social_post(self, platform: str, topic: str, content: str):
        if not self.user_id: return None
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO social_posts (user_id, platform, topic, content, status) VALUES (?, ?, ?, ?, 'Pending')",
                (self.user_id, platform, topic, content)
            )
            conn.commit()
            return cursor.lastrowid

    def get_pending_social_posts(self):
        if not self.user_id: return []
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM social_posts WHERE status = 'Pending' AND user_id = ? ORDER BY timestamp DESC", (self.user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def log_agent_output(self, crew_name: str, output: str, status: str = 'Success', execution_time: float = None, metadata: str = None, tokens_used: int = None):
        if not self.user_id: return
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO agent_outputs (user_id, crew_name, output, status, execution_time, metadata, tokens_used) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (self.user_id, crew_name, output, status, execution_time, metadata, tokens_used)
            )
            conn.commit()

    def get_all_agent_outputs(self):
        if not self.user_id: return []
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agent_outputs WHERE user_id = ? ORDER BY timestamp DESC", (self.user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def update_social_post(self, post_id: int, status: str, content: str = None):
        if not self.user_id: return
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if content is not None:
                cursor.execute(
                    "UPDATE social_posts SET status = ?, content = ? WHERE id = ? AND user_id = ?",
                    (status, content, post_id, self.user_id)
                )
            else:
                cursor.execute(
                    "UPDATE social_posts SET status = ? WHERE id = ? AND user_id = ?",
                    (status, post_id, self.user_id)
                )
            conn.commit()

    def get_pending_leads(self):
        if not self.user_id: return []
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM leads WHERE status = 'Pending' AND user_id = ?", (self.user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def update_lead_status(self, lead_id, status, summary=None):
        if not self.user_id: return
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if summary:
                cursor.execute(
                    "UPDATE leads SET status = ?, research_summary = ?, updated_at = ? WHERE id = ? AND user_id = ?",
                    (status, summary, datetime.now(), lead_id, self.user_id)
                )
            else:
                cursor.execute(
                    "UPDATE leads SET status = ?, updated_at = ? WHERE id = ? AND user_id = ?",
                    (status, datetime.now(), lead_id, self.user_id)
                )
            conn.commit()

    def log_telephony(self, lead_id, provider, sid, call_type, result, transcript=None):
        if not self.user_id: return
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO telephony_logs (user_id, lead_id, provider, sid, type, result, transcript) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (self.user_id, lead_id, provider, sid, call_type, result, transcript)
            )
            conn.commit()

    def get_all_leads(self):
        if not self.user_id: return []
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM leads WHERE user_id = ? ORDER BY created_at DESC", (self.user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_telephony_logs(self):
        if not self.user_id: return []
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT l.name, l.phone, t.id, t.provider, t.type, t.result, t.transcript, t.timestamp 
                FROM telephony_logs t
                JOIN leads l ON t.lead_id = l.id
                WHERE t.user_id = ?
                ORDER BY t.timestamp DESC
            """, (self.user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def update_transcript(self, log_id, transcript):
        if not self.user_id: return
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE telephony_logs SET transcript = ? WHERE id = ? AND user_id = ?",
                (transcript, log_id, self.user_id)
            )
            conn.commit()

    # --- Custom Agents Database Methods ---
    def save_agent(self, name: str, role: str, goal: str, backstory: str, temperature: float = 0.7, tools: str = ""):
        if not self.user_id: return
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO custom_agents (user_id, name, role, goal, backstory, temperature, tools) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (self.user_id, name, role, goal, backstory, temperature, tools)
            )
            conn.commit()

    def get_all_agents(self):
        if not self.user_id: return []
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM custom_agents WHERE user_id = ? ORDER BY id DESC", (self.user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def delete_agent(self, agent_id: int):
        if not self.user_id: return
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM custom_agents WHERE id = ? AND user_id = ?", (agent_id, self.user_id))
            conn.commit()

    # --- Custom Tasks Database Methods ---
    def save_task(self, name: str, description: str, expected_output: str, agent_name: str = ""):
        if not self.user_id: return
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO custom_tasks (user_id, name, description, expected_output, agent_name) VALUES (?, ?, ?, ?, ?)",
                (self.user_id, name, description, expected_output, agent_name)
            )
            conn.commit()

    def get_all_tasks(self):
        if not self.user_id: return []
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM custom_tasks WHERE user_id = ? ORDER BY timestamp DESC", (self.user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def delete_task(self, task_id: int):
        if not self.user_id: return
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM custom_tasks WHERE id = ? AND user_id = ?", (task_id, self.user_id))
            conn.commit()

    # --- Human-in-the-Loop Interceptor ---
    def create_pending_action(self, tool_name: str, details: str):
        if not self.user_id: return None
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO pending_actions (user_id, tool_name, action_details, status) VALUES (?, ?, ?, 'Pending')",
                (self.user_id, tool_name, details)
            )
            conn.commit()
            return cursor.lastrowid

    def check_action_status(self, action_id: int):
        if not self.user_id: return 'Rejected', 'No user ID'
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT status, feedback FROM pending_actions WHERE id = ? AND user_id = ?", (action_id, self.user_id))
            row = cursor.fetchone()
            if row:
                return row['status'], row['feedback']
            return 'Rejected', 'Action not found'

    def get_all_pending_actions(self):
        if not self.user_id: return []
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pending_actions WHERE status = 'Pending' AND user_id = ? ORDER BY timestamp DESC", (self.user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def resolve_action(self, action_id: int, status: str, feedback: str = None):
        if not self.user_id: return
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE pending_actions SET status = ?, feedback = ? WHERE id = ? AND user_id = ?",
                (status, feedback, action_id, self.user_id)
            )
            conn.commit()
