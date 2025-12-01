import os
import logging
import tempfile
import asyncio
from pathlib import Path

from openai import OpenAI
from config import OPENAI_API_KEY


# Client
client = OpenAI(api_key=OPENAI_API_KEY)


# -------------------------------------------------------------
# Split large files into chunks (100 MB)
# -------------------------------------------------------------
def split_to_chunks(input_path: str, chunk_size_mb: int = 100) -> list[str]:
    input_path = Path(input_path)
    output_files = []

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
# Transcribe single chunk
# -------------------------------------------------------------
async def transcribe_single_chunk(path: str) -> str:
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
# Create MD structure + summary
# -------------------------------------------------------------
async def generate_structure_and_summary(full_text: str) -> tuple[str, str]:
    prompt = f"""
Ты — профессиональный редактор и конспектолог.

На основе транскрипта создай:

1) Структурированный MD-конспект:
   - Заголовки
   - Подзаголовки
   - Списки
   - Без таймкодов

2) Краткое Summary (5–10 предложений).

Текст:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content

    if "Summary:" in answer:
        parts = answer.split("Summary:", 1)
        return parts[0].strip(), parts[1].strip()

    return answer, "Summary не найдено."


# -------------------------------------------------------------
# Main function
# -------------------------------------------------------------
async def process_audio_or_video(file_path: str) -> tuple[str, str, str]:
    logging.info(f"🎧 Начинаю обработку файла: {file_path}")

    chunks = split_to_chunks(file_path, chunk_size_mb=100)
    logging.info(f"Файл разбит на {len(chunks)} частей")

    full_text = ""

    # Transcribe each chunk
    for idx, chunk in enumerate(chunks):
        logging.info(f"⏳ Транскрибирую чанк {idx+1}/{len(chunks)}: {chunk}")
        text = await transcribe_single_chunk(chunk)
        full_text += "\n" + text

    logging.info("Создаю структуру и summary...")

    structured_md, summary = await generate_structure_and_summary(full_text)

    # Cleanup
    try:
        for c in chunks:
            os.remove(c)
    except:
        pass

    return full_text, structured_md, summary
