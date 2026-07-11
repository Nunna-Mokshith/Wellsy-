"""
Wellsy RAG Ingestion & Query Pipeline
Manages document reading (TXT, PDF, DOCX), chunking, SQLite storage,
and vector similarity searching.
"""
import os
import sqlite3
import re
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
from google import genai
from google.genai import types

# Setup pathing
WELLSY_ROOT = Path(__file__).parent.parent.parent
DB_PATH = WELLSY_ROOT / "backend" / "db" / "wellsy.db"
STORAGE_DIR = WELLSY_ROOT / "storage"
os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(DB_PATH.parent, exist_ok=True)

# API Setup
from dotenv import load_dotenv
load_dotenv(WELLSY_ROOT / ".env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


def get_db_connection():
    """Create connection to SQLite and initialize schema."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    # Setup tables
    conn.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT UNIQUE,
        file_name TEXT,
        file_type TEXT,
        last_modified REAL
    );
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_id INTEGER,
        chunk_index INTEGER,
        content TEXT,
        embedding BLOB,
        FOREIGN KEY(doc_id) REFERENCES documents(id) ON DELETE CASCADE
    );
    """)
    conn.commit()
    return conn


def get_embedding(text: str) -> List[float]:
    """Generate float vector embedding using models/gemini-embedding-001."""
    if not GEMINI_API_KEY:
        return [0.0] * 768
    
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.embed_content(
            model="models/gemini-embedding-001",
            contents=text
        )
        # Handle embedding formats
        if response.embeddings:
            return response.embeddings[0].values
    except Exception as e:
        print(f"[RAG] Embedding generation error: {e}")
    return [0.0] * 768


def extract_text_from_file(file_path: Path) -> str:
    """Extract plain text from TXT, PDF or DOCX."""
    suffix = file_path.suffix.lower()
    
    if suffix == '.txt':
        return file_path.read_text(encoding='utf-8', errors='replace')
        
    elif suffix == '.pdf':
        try:
            import PyPDF2
            text = []
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    t = page.extract_text()
                    if t:
                        text.append(t)
            return "\n".join(text)
        except Exception as e:
            return f"Error reading PDF: {e}"
            
    elif suffix == '.docx':
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            return f"Error reading DOCX: {e}"
            
    return ""


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """Splits text into chunks with words overlapping."""
    words = text.split()
    chunks = []
    
    if len(words) <= chunk_size:
        return [text]
        
    i = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunks.append(" ".join(chunk_words))
        i += chunk_size - overlap
        
    return chunks


def index_file(file_path_str: str) -> str:
    """Read, chunk, generate embeddings, and index a file into SQLite."""
    file_path = Path(file_path_str).resolve()
    if not file_path.exists():
        return f"File does not exist: {file_path_str}"
        
    conn = get_db_connection()
    try:
        mod_time = file_path.stat().st_mtime
        
        # Check if already indexed and unchanged
        cursor = conn.execute("SELECT id, last_modified FROM documents WHERE file_path = ?", (str(file_path),))
        row = cursor.fetchone()
        
        if row:
            if row['last_modified'] >= mod_time:
                conn.close()
                return f"Skipped: {file_path.name} is already indexed and up-to-date."
            # Delete old chunks
            conn.execute("DELETE FROM chunks WHERE doc_id = ?", (row['id'],))
            conn.execute("DELETE FROM documents WHERE id = ?", (row['id'],))
            conn.commit()
            
        # Extract and Index
        text = extract_text_from_file(file_path)
        if not text.strip():
            conn.close()
            return f"No text could be extracted from {file_path.name}"
            
        chunks = chunk_text(text)
        
        cursor = conn.execute(
            "INSERT INTO documents (file_path, file_name, file_type, last_modified) VALUES (?, ?, ?, ?)",
            (str(file_path), file_path.name, file_path.suffix, mod_time)
        )
        doc_id = cursor.lastrowid
        
        for idx, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            # Serialize float array to float32 blob
            emb_blob = np.array(embedding, dtype=np.float32).tobytes()
            conn.execute(
                "INSERT INTO chunks (doc_id, chunk_index, content, embedding) VALUES (?, ?, ?, ?)",
                (doc_id, idx, chunk, emb_blob)
            )
            
        conn.commit()
        return f"Successfully indexed {file_path.name} ({len(chunks)} chunks)."
    except Exception as e:
        return f"Failed to index {file_path.name}: {e}"
    finally:
        conn.close()


def sync_storage_folder() -> List[str]:
    """Scan D:\\Wellsy\\storage and index all documents using compiled C++ file scanner."""
    results = []
    supported_extensions = {'.txt', '.pdf', '.docx'}
    
    try:
        from tools.fast_scanner import fast_scan
        print("[RAG] Utilizing C++ directory traversal engine...")
        scanned_files = fast_scan(str(STORAGE_DIR))
        for item in scanned_files:
            file_path = Path(item["path"])
            if file_path.suffix.lower() in supported_extensions:
                res = index_file(str(file_path))
                results.append(res)
    except Exception as e:
        print(f"[RAG] Fallback to Python traversal due to error: {e}")
        # Standard Python path fallback
        for item in STORAGE_DIR.iterdir():
            if item.is_file() and item.suffix.lower() in supported_extensions:
                res = index_file(str(item))
                results.append(res)
            
    return results


def query_rag(query_text: str, top_k: int = 4) -> List[Dict[str, Any]]:
    """Embedding search logic with similarity score over local SQLite database."""
    query_vector = get_embedding(query_text)
    query_np = np.array(query_vector, dtype=np.float32)
    
    conn = get_db_connection()
    cursor = conn.execute("""
        SELECT chunks.content, chunks.chunk_index, chunks.embedding, 
               documents.file_name, documents.file_path 
        FROM chunks 
        JOIN documents ON chunks.doc_id = documents.id
    """)
    rows = cursor.fetchall()
    
    results = []
    for row in rows:
        emb_blob = row['embedding']
        if not emb_blob:
            continue
            
        # Recover float array
        stored_vector = np.frombuffer(emb_blob, dtype=np.float32)
        
        # Calculate cosine similarity
        dot_product = np.dot(query_np, stored_vector)
        norm_q = np.linalg.norm(query_np)
        norm_s = np.linalg.norm(stored_vector)
        
        similarity = 0.0
        if norm_q > 0 and norm_s > 0:
            similarity = float(dot_product / (norm_q * norm_s))
            
        results.append({
            "content": row['content'],
            "file_name": row['file_name'],
            "file_path": row['file_path'],
            "chunk_index": row['chunk_index'],
            "similarity": similarity
        })
        
    conn.close()
    
    # Sort and return top results
    results.sort(key=lambda x: x['similarity'], reverse=True)
    return results[:top_k]
