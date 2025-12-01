import os
import logging
import tempfile
import asyncio
from pathlib import Path

from openai import OpenAI
from config import OPENAI_API_KEY


client = OpenAI(api_key=OPENAI_API_KEY)


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
            idx += 0

    return output_files


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
        logging.error(f"Error transcribing chunk {path}: {e}")
        return ""


async def generate_structure_and_summary(full_text: str) -> tuple[str, str]:
    prompt = (
        "Ты — профессиональный редактор и конспектолог.\n"
        "Создай:\n"
        "1) Структурированный MD-конспект:\n"
        "   - Заголовки\n"
        "   - Подзаголовки\n"
        "   - Списки\n"
        "   - Ключевые мысли\n"
        "   - Без таймкодов\n"
        "\n2) Краткое Summary (5–10 предложений)\n"
        "\nТекст:\n"
        f"{full_text}"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content

    if "Summary:" in answer:
        structured, summary = answer.split("Summary:", 1)
        return structured.strip(), summary.strip()

    return answer, "Summary not found."


async def process_audio_or_video(file_path: str) -> tuple[str, str, str]:
    logging.info(f"Starting processing: {file_path}")

    chunks = split_to_chunks(file_path, chunk_size_mb=100)
    logging.info(f"File split into {len(chunks)} chunks")

    full_text = ""

    for idx, chunk in enumerate(chunks):
        logging.info(f"Transcribing chunk {idx+1}/{len(chunks)}: {chunk}")
        text = await transcribe_single_chunk(chunk)
        full_text += "\n" + text

    logging.info("Generating structure and summary...")

    structured_md, summary = await generate_structure_and_summary(full_text)

    try:
        for c in chunks:
            os.remove(c)
    except:
        pass

    return full_text, structured_md, summary
