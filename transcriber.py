import os
import asyncio
import subprocess
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ------------------------------
# Конвертация видео в аудио WAV
# ------------------------------
async def convert_to_wav(video_path: str) -> str:
    audio_path = video_path.replace(".mp4", ".wav")

    command = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        audio_path
    ]

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    await process.communicate()

    return audio_path


# ------------------------------
# Отправка на транскрибацию
# ------------------------------
async def transcribe_audio(video_path: str) -> str:
    # конвертация в WAV
    wav_path = await convert_to_wav(video_path)

    # отправляем WAV в OpenAI
    with open(wav_path, "rb") as f:
        response = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=f,
            response_format="text"
        )

    text = response

    # очищаем аудио
    if os.path.exists(wav_path):
        os.remove(wav_path)

    return text
