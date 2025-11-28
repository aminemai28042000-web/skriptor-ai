import os
import asyncio
import subprocess
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---------------------------------------------------------
# Конвертация видео в WAV (идеально для распознавания)
# ---------------------------------------------------------
async def convert_video_to_wav(video_path: str) -> str:
    wav_path = video_path.rsplit(".", 1)[0] + ".wav"

    command = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-acodec", "pcm_s16le",
        wav_path
    ]

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    await process.communicate()
    return wav_path


# ---------------------------------------------------------
# Транскрипция аудио через OpenAI
# ---------------------------------------------------------
async def transcribe_audio(video_path: str) -> str:
    # 1. конвертируем в wav
    wav_path = await convert_video_to_wav(video_path)

    # 2. Отправляем в OpenAI Whisper
    with open(wav_path, "rb") as f:
        response = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=f,
            response_format="text"
        )

    # 3. Стираем временный файл
    if os.path.exists(wav_path):
        os.remove(wav_path)

    return response
