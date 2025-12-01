import os
import logging
import tempfile
import asyncio
import subprocess
from pathlib import Path

from openai import OpenAI
from config import OPENAI_API_KEY


# Инициализация клиента OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)


# -------------------------------------------------------------
# Вспомогательная функция: разрезать большие файлы на части
# -------------------------------------------------------------
def split_to_chunks(input_path: str, chunk_size_mb: int = 100) -> list[str]:
    """
    Разрезает входной файл на части по 100 МБ (или сколько указано).
    Whisper умеет стабильно работать с такими размерами.
    """
    input_path = Path(input_path)
    output_files = []

    # размер части в байтах
    chunk_bytes = chunk_size_mb * 1024 * 1024

    with open(input_path, "rb") as source:
        idx = 0
        while True:
            data = source.read(chunk_bytes)
            if not data:
                break

            part_path = input_path.parent / f"{input_path.stem}_part{idx}{input_path.suffix}"
            with open(part_path, "wb") as f:
                f.write(data)

            output_files.append(str(part_path))
            idx += 1

    return output_files


# -------------------------------------------------------------
# Транскрипция одного чанка
# -------------------------------------------------------------
async def transcribe_single_chunk(path: str) -> str:
    """
    Отправляет один файл‐чанк в OpenAI Whisper.
    """
    try:
        with open(path, "rb") as f:
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text"
            )
        return result
    except Exception as e:
        logging.error(f"Ошибка транскрибирования чанка {path}: {e}")
        return ""


# -------------------------------------------------------------
# Генерация структуры (markdown) + summary
# -------------------------------------------------------------
async def generate_structure_and_summary(full_text: str) -> tuple[str, str]:
    """
    GPT формирует:
    - структурированный markdown
    - короткое summary
    """

    prompt = f"""
Ты — профессиональный редактор и конспектолог.

На вход даю расшифровку видео. Создай:

1) Чистый структурированный конспект (markdown)
   - заголовки
   - подзаголовки
   - списки
   - ключевые мысли
   - временные маркеры убрать

2) Краткое Summary (5–10 предложений)

Текст для обработки:
