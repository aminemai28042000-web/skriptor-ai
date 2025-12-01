import os
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


async def process_audio_or_video(file_path: str) -> str:
    """
    Асинхронная обёртка над синхронным Whisper API,
    чтобы не блокировать event loop.
    """

    try:
        # Whisper в новом SDK работает синхронно → оборачиваем в asyncio.to_thread
        def _transcribe():
            with open(file_path, "rb") as f:
                response = client.audio.transcriptions.create(
                    file=f,
                    model="whisper-1"
                )
            return response.text.strip()

        text = await asyncio.to_thread(_transcribe)
        return text

    except Exception as e:
        return f"Ошибка транскрибации: {str(e)}"
