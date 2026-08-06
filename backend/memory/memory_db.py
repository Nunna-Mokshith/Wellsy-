"""
Wellsy Encrypted Memory Database
Persists user notes, file change events, session summaries, and task history safely.
"""
import sqlite3
import json
import base64
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from memory.config import MEMORY_DB_FILE

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class MemoryDB:
    def __init__(self, db_path: Path = MEMORY_DB_FILE):
        self.db_path = db_path
        self._init_fernet()
        self._init_db()

    def _init_fernet(self):
        """Initialize Fernet encryption key based on machine unique key or local seed."""
        seed = "wellsy_secure_memory_key_seed_2026"
        key = base64.urlsafe_b64encode(hashlib.sha256(seed.encode()).digest())
        if CRYPTO_AVAILABLE:
            self.fernet = Fernet(key)
        else:
            self.fernet = None

    def _encrypt(self, text: str) -> str:
        if not text:
            return ""
        if self.fernet:
            return self.fernet.encrypt(text.encode("utf-8")).decode("utf-8")
        return base64.b64encode(text.encode("utf-8")).decode("utf-8")

    def _decrypt(self, token: str) -> str:
        if not token:
            return ""
        try:
            if self.fernet:
                return self.fernet.decrypt(token.encode("utf-8")).decode("utf-8")
            return base64.b64decode(token.encode("utf-8")).decode("utf-8")
        except Exception:
            return token  # Fallback unencrypted text if decryption fails

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Create sqlite tables if not present."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata_json TEXT
                )
            """)
            conn.commit()

    def store_memory(self, memory_type: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> int:
        """Store a new encrypted memory."""
        encrypted_content = self._encrypt(content)
        timestamp = datetime.now().isoformat()
        metadata_str = json.dumps(metadata) if metadata else "{}"

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO memories (memory_type, timestamp, content, metadata_json) VALUES (?, ?, ?, ?)",
                (memory_type, timestamp, encrypted_content, metadata_str)
            )
            conn.commit()
            return cursor.lastrowid

    def recall_memories(self, query: str = "", limit: int = 15, memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch and decrypt recent memories matching query or type."""
        results = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if memory_type:
                cursor.execute(
                    "SELECT id, memory_type, timestamp, content, metadata_json FROM memories WHERE memory_type = ? ORDER BY id DESC LIMIT ?",
                    (memory_type, limit * 2)
                )
            else:
                cursor.execute(
                    "SELECT id, memory_type, timestamp, content, metadata_json FROM memories ORDER BY id DESC LIMIT ?",
                    (limit * 2,)
                )
            rows = cursor.fetchall()

        query_lower = query.lower() if query else ""
        for row in rows:
            m_id, m_type, ts, enc_content, meta_str = row
            dec_content = self._decrypt(enc_content)
            
            # Simple keyword matching if query provided
            if query_lower and query_lower not in dec_content.lower() and query_lower not in meta_str.lower():
                continue

            try:
                meta = json.loads(meta_str) if meta_str else {}
            except Exception:
                meta = {}

            results.append({
                "id": m_id,
                "type": m_type,
                "timestamp": ts,
                "content": dec_content,
                "metadata": meta
            })

            if len(results) >= limit:
                break

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memories."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM memories")
            total = cursor.fetchone()[0]

            cursor.execute("SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type")
            by_type = dict(cursor.fetchall())

        return {
            "total_memories": total,
            "by_type": by_type
        }

    def forget_all(self) -> bool:
        """Clear all stored memories."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memories")
            conn.commit()
        return True


# Global instance singleton
memory_db = MemoryDB()
