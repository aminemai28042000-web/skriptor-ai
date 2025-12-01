import os
from openai import OpenAI
from config import OPENAI_API_KEY, TEMP_DIR

client = OpenAI(api_key=OPENAI_API_KEY)


async def process_audio_or_video(file_path: str) -> str:
    """
    Универсальная функция транскрибации аудио/видео.
    Преобразует входной файл в текст через OpenAI Whisper.
    """

    try:
        with open(file_path, "rb") as f:
            response = client.audio.transcriptions.create(
                file=f,
                model="whisper-1",
            )

        text = response.text.strip()
        return text

    except Exception as e:
        return f"Ошибка транскрибации: {str(e)}"
