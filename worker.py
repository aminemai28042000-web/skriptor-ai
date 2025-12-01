import asyncio
import os
from worker_queue import dequeue_task
from link_downloader import download_file_with_progress
from transcriber import transcribe_audio
from formatter import format_text
from utils import safe_send_message
from bot import bot
from config import TEMP_DIR

async def worker_loop():
    while True:
        task = await dequeue_task()

        if not task:
            await asyncio.sleep(1)
            continue

        chat_id = task["chat_id"]
        url = task["url"]

        temp_file = os.path.join(TEMP_DIR, "downloaded.mp4")

        try:
            await safe_send_message(bot, chat_id, "⏳ Начинаю скачивание…")

            await download_file_with_progress(url, temp_file)

            await safe_send_message(bot, chat_id, "⏳ Расшифровка…")
            text = await transcribe_audio(temp_file)

            result = format_text(text)

            await safe_send_message(bot, chat_id, "Готово!\n\n" + result)

        except Exception as e:
            await safe_send_message(bot, chat_id, f"Ошибка: {str(e)}")

        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == "__main__":
    asyncio.run(worker_loop())
