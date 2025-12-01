# utils.py
"""
Вспомогательные функции для Скриптор AI:
- логирование
- проверка размера файла
- генерация временных путей
- извлечение расширений
- человеко-читаемые размеры
"""

import os
import time
import uuid
import math
from datetime import datetime


# -------------------------------
# ЛОГИ
# -------------------------------

def log(msg: str):
    """Красивый вывод логов в консоль Render."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}", flush=True)


# -------------------------------
# РАБОТА С РАЗМЕРАМИ
# -------------------------------

def get_file_size(path: str) -> int:
    """Возвращает размер файла в байтах."""
    try:
        return os.path.getsize(path)
    except:
        return 0


def human_size(num_bytes: int) -> str:
    """Переводит байты → читаемый формат."""
    if num_bytes < 1024:
        return f"{num_bytes} B"
    for unit in ["KB", "MB", "GB", "TB"]:
        num_bytes /= 1024
        if num_bytes < 1024:
            return f"{num_bytes:.2f} {unit}"
    return f"{num_bytes:.2f} PB"


def ensure_max_size(path: str, limit_gb: int = 2) -> bool:
    """Проверяет, что файл ≤ лимита (по умолчанию 2GB)."""
    size = get_file_size(path)
    return size <= limit_gb * 1024 * 1024 * 1024


# -------------------------------
# ВРЕМЕННЫЕ ПАПКИ И ФАЙЛЫ
# -------------------------------

def temp_name(ext=""):
    """Создает уникальное имя файла."""
    uid = uuid.uuid4().hex
    if ext and not ext.startswith("."):
        ext = "." + ext
    return f"/tmp/{uid}{ext}"


def extract_extension(filename: str) -> str:
    """Извлекает расширение файла → 'mp4', 'mov', 'mp3', 'wav'."""
    if "." not in filename:
        return ""
    return filename.lower().split(".")[-1]


def safe_filename(base: str, ext: str) -> str:
    """Создаёт безопасное имя файла."""
    base = base.replace(" ", "_").replace("/", "_")
    if not ext.startswith("."):
        ext = "." + ext
    return f"{base}{ext}"


# -------------------------------
# ПРОГРЕСС
# -------------------------------

def percent(current: int, total: int) -> int:
    """Высчитывает % загрузки/обработки."""
    if total == 0:
        return 0
    return math.floor((current / total) * 100)


def progress_bar(p: int) -> str:
    """Текстовая шкала прогресса."""
    blocks = math.floor(p / 10)
    bar = "█" * blocks + "—" * (10 - blocks)
    return f"[{bar}] {p}%"


# -------------------------------
# ПАУЗЫ
# -------------------------------

def sleep(ms: int):
    """Удобная пауза в миллисекундах."""
    time.sleep(ms / 1000)
