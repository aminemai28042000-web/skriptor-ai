import os
import asyncio
from openai import OpenAI

client = OpenAI()

async def process_audio_or_video(path: str):
    """
    Аудио/видео → текст + summary
    """
    loop = asyncio.get_running_loop()

    def transcribe():
        with open(path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=f
            )
            summary = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"Суммаризируй текст:\n\n{transcript.text}"}]
            )
            return transcript.text, summary.choices[0].message.content

    text, summ = await loop.run_in_executor(None, transcribe)
    return text, summ
