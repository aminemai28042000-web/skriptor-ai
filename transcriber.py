import os
import asyncio
from openai import OpenAI

client = OpenAI()

async def process_audio_or_video(path: str):
    loop = asyncio.get_running_loop()

    def _run():
        # Транскрибация
        with open(path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=f
            )

        text = transcript.text

        # Summary
        summary = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": f"Сделай краткое, структурированное summary по тексту:\n\n{text}"
                }
            ]
        )

        return text, summary.choices[0].message.content

    return await loop.run_in_executor(None, _run)
