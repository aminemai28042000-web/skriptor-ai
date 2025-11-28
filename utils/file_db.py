import sqlite3
import os
from datetime import datetime

DB_PATH = "skriptor.db"


# ---------------------------------------------------------
# Создание базы при старте
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Таблица пользователей
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_seen TEXT
    )
    """)

    # Таблица запросов
    cur.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        source TEXT,
        file_size_mb REAL,
        pdf_path TEXT,
        md_path TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# Регистрация нового пользователя
# ---------------------------------------------------------
def register_user(user_id: int, username: str = None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    exists = cur.fetchone()

    if not exists:
        cur.execute(
            "INSERT INTO users (user_id, username, first_seen) VALUES (?, ?, ?)",
            (user_id, username, datetime.now().isoformat())
        )

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# Логируем обработанный файл
# ---------------------------------------------------------
def log_file(user_id: int, source: str, size: float, pdf: str, md: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO files (user_id, source, file_size_mb, pdf_path, md_path, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, source, size, pdf, md, datetime.now().isoformat())
    )

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# Количество пользователей
# ---------------------------------------------------------
def get_user_count() -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]

    conn.close()
    return count


# ---------------------------------------------------------
# Количество обработанных видео
# ---------------------------------------------------------
def get_file_count() -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM files")
    count = cur.fetchone()[0]

    conn.close()
    return count


# ---------------------------------------------------------
# Последние N обработанных файлов
# ---------------------------------------------------------
def get_last_files(limit: int = 10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    SELECT users.username, files.source, files.pdf_path, files.created_at
    FROM files
    JOIN users ON users.user_id = files.user_id
    ORDER BY files.id DESC
    LIMIT ?
    """, (limit,))

    rows = cur.fetchall()
    conn.close()
    return rows
