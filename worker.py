import os
import asyncio
import logging
import json
import redis.asyncio as aioredis

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.types import FSInputFile

from config import BOT_TOKEN, REDIS_URL
from link_downloader import download_file_with_progress
from transcriber import process_audio_or_video
from file_generators import create_pdf, create_markdown


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="WORKER | %(asctime)s | %(levelname)s | %(message)s",
)

# ---------------------------------------------------------
# Init bot + redis
# ---------------------------------------------------------
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)


# ---------------------------------------------------------
# Queue processing
# ---------------------------------------------------------
async def worker_loop():
    logging.info("✔ WORKER STARTED — waiting for tasks...")

    while True:
        try:
            item = await redis_client.blpop("task_queue", timeout=5)

            if not item:
                continue  # no tasks

            _, raw_data = item
            update = json.loads(raw_data)

            await handle_update(update)

        except Exception as e:
            logging.error(f"❌ WORKER LOOP ERROR: {e}")
            await asyncio.sleep(2)


# ---------------------------------------------------------
# Main handler
# ---------------------------------------------------------
async def handle_update(update):
    """
    В update приходит JSON Telegram Update, который мы получили через вебхук.
    Здесь мы проверяем какие поля есть — фото/видео/документ/сообщение со ссылкой.
    """

    message = update.get("message")
    if not message:
        return

    chat_id = message["chat"]["id"]

    # -------- 1. LINK from text --------
    if "text" in message and message["text"].startswith("http"):
        url = message["text"].strip()
        await bot.send_message(chat_id, "🔗 Обнаружена ссылка. Скачиваю файл...")

        temp_path = await download_file_with_progress(
            bot, chat_id, url
        )

        if temp_path is None:
            await bot.send_message(chat_id, "❌ Не удалось скачать файл по ссылке.")
            return

        await process_and_send(chat_id, temp_path)
        return

    # -------- 2. VIDEO or DOCUMENT --------
    if "video" in message:
        file_id = message["video"]["file_id"]
        await handle_telegram_file(chat_id, file_id)
        return

    if "document" in message:
        file_id = message["document"]["file_id"]
        await handle_telegram_file(chat_id, file_id)
        return

    # -------- 3. Unsupported --------
    await bot.send_message(
        chat_id,
        "⚠ Пожалуйста, пришлите видео/аудио/файл или ссылку.",
    )


# ---------------------------------------------------------
# Download Telegram file
# ---------------------------------------------------------
async def handle_telegram_file(chat_id, file_id):
    try:
        await bot.send_message(chat_id, "📥 Получил файл. Скачиваю...")

        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path

        # Telegram CDN direct URL
        url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

        temp_path = await download_file_with_progress(
            bot, chat_id, url
        )

        if temp_path is None:
            await bot.send_message(chat_id, "❌ Ошибка скачивания.")
            return

        await process_and_send(chat_id, temp_path)

    except Exception as e:
        logging.error(f"❌ Error downloading Telegram file: {e}")
        await bot.send_message(chat_id, "❌ Ошибка обработки файла.")


# ---------------------------------------------------------
# Process: transcription → PDF + MD → send to user
# ---------------------------------------------------------
async def process_and_send(chat_id, file_path):
    try:
        await bot.send_message(chat_id, "🔧 Обрабатываю файл... Это может занять время.")

        transcript_text, structured_text = await process_audio_or_video(file_path)

        # --- create files
        pdf_path = create_pdf(structured_text)
        md_path = create_markdown(transcript_text, structured_text)

        # --- send files
        await bot.send_message(chat_id, "📤 Отправляю результаты...")

        await bot.send_document(
            chat_id,
            FSInputFile(pdf_path, filename="result.pdf")
        )
        await bot.send_document(
            chat_id,
            FSInputFile(md_path, filename="result.md")
        )

        await bot.send_message(chat_id, "✨ Готово! Спасибо за использование «Скриптор AI».")

    except Exception as e:
        logging.error(f"❌ PROCESS ERROR: {e}")
        await bot.send_message(chat_id, "❌ Ошибка обработки файла.")

    finally:
        # cleanup temp files
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass


# ---------------------------------------------------------
# ENTRYPOINT
# ---------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(worker_loop())
