import asyncio
import os
from openai import OpenAI
from config import OPENAI_API_KEY

# -------------------------------
# Render FIX — отключаем системные прокси
# -------------------------------
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("ALL_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)
os.environ.pop("all_proxy", None)

# -------------------------------
# OpenAI клиент
# -------------------------------
client = OpenAI(api_key=OPENAI_API_KEY)


async def process_audio_or_video(file_path: str) -> str:
    """Асинхронная транскрибация аудио/видео через Whisper."""

    def _transcribe():
        try:
            with open(file_path, "rb") as f:
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f
                )
            return response.text.strip()
        except Exception as e:
            return f"Ошибка транскрибации: {str(e)}"

    return await asyncio.to_thread(_transcribe)
