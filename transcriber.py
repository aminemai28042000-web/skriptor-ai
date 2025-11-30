import os
import asyncio
from openai import OpenAI

client = OpenAI()

async def process_audio_or_video(path: str):
    """
    Принимает путь к файлу (до 2 ГБ).
    Выполняет транскрибацию + делает summary.
    Возвращает: (текст транскрипта, summary)
    """

    loop = asyncio.get_running_loop()

    def _run():
        # --- ТРАНСКРИПЦИЯ ---
        with open(path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=f
            )

        text = transcript.text

        # --- SUMMARY ---
        summary = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": f"Сделай краткое, структурированное summary по тексту ниже:\n\n{text}"
                }
            ]
        )

        return text, summary.choices[0].message.content

    # Запуск в executor — чтобы не блокировать бота
    result = await loop.run_in_executor(None, _run)
    return result  # (text, summary)
