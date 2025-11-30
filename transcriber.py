import os
import aiofiles
import asyncio
from openai import AsyncOpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=OPENAI_API_KEY)


# ------------------------
# ЧТЕНИЕ ФАЙЛА (ASYNC)
# ------------------------
async def read_file_async(path: str) -> bytes:
    async with aiofiles.open(path, "rb") as f:
        return await f.read()


# ------------------------
# ТРАНСКРИПЦИЯ
# ------------------------
async def transcribe_audio(path: str) -> str:
    try:
        file_bytes = await read_file_async(path)

        transcript = await client.audio.transcriptions.create(
            model="whisper-1",
            file=("audio.mp3", file_bytes),
            response_format="text"
        )

        return transcript

    except Exception as e:
        print("TRANSCRIBE ERROR:", e)
        return None


# ------------------------
# САММАРИ
# ------------------------
async def make_summary(text: str) -> str:
    try:
        prompt = (
            "Сделай структурированное, короткое и информативное summary текста. "
            "В виде блоков: \n"
            "1) Краткое содержание \n"
            "2) Ключевые тезисы \n"
            "3) Что важно запомнить \n"
            "4) Кому может быть полезно"
        )

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты профессиональный аналитик текста."},
                {"role": "user", "content": prompt + "\n\nТекст:\n" + text}
            ],
            max_tokens=1500
        )

        return response.choices[0].message.content

    except Exception as e:
        print("SUMMARY ERROR:", e)
        return "Summary недоступно."


# ------------------------
# ОБЩАЯ ОБРАБОТКА ФАЙЛА
# ------------------------
async def process_audio_or_video(path: str):
    """
    Главная функция:
    - принимает путь к аудио/видео
    - делает транскрибацию
    - делает summary
    - возвращает transcript + summary
    """

    transcript = await transcribe_audio(path)

    if not transcript:
        return None, None

    summary = await make_summary(transcript)

    return transcript, summary
