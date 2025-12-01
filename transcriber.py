import os
from openai import OpenAI
from config import OPENAI_API_KEY

# В v1.x клиент создаётся БЕЗ api_key
client = OpenAI()

async def process_audio_or_video(file_path: str) -> str:
    """
    Универсальная транскрипция аудио/видео.
    """
    with open(file_path, "rb") as f:
        response = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=f
        )

    return response.text
