import asyncio
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


async def process_audio_or_video(file_path: str) -> str:
    """
    Асинхронная транскрибация аудио/видео с Whisper.
    Оборачиваем синхронный вызов Whisper в asyncio.to_thread(),
    чтобы worker не зависал.
    """

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

    # выполняем синхронный код в отдельном потоке
    return await asyncio.to_thread(_transcribe)
