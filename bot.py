import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from aiogram.filters import CommandStart

from transcriber import process_audio_or_video
from link_downloader import download_from_link
from file_generators import generate_pdf, generate_markdown
from formatter import format_transcript

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Очередь задач (ограничение — 1 одновременная)
task_queue = asyncio.Queue()
processing = False


# -------------------------------
#   Обёртка очереди
# -------------------------------
async def queue_worker():
    global processing
    if processing:
        return
    processing = True

    while not task_queue.empty():
        user_id, coro = await task_queue.get()
        try:
            await coro
        except Exception as e:
            await bot.send_message(user_id, f"❌ Ошибка обработки: {e}")
        await asyncio.sleep(0.1)

    processing = False


async def enqueue(message: types.Message, coro):
    await task_queue.put((message.from_user.id, coro))
    await queue_worker()


# -------------------------------
#   Команда /start
# -------------------------------
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("👋 Отправьте аудио, видео или ссылку (YouTube / соц. сети / прямой URL)")


# -------------------------------
#   Приём медиа
# -------------------------------
@dp.message(lambda m: m.video or m.audio or m.document)
async def handle_media(message: types.Message):

    await message.answer("🔄 Загружаю файл, подождите...")

    async def task():
        file_info = None
        if message.document:
            file_info = await bot.get_file(message.document.file_id)
            filename = message.document.file_name
        elif message.video:
            file_info = await bot.get_file(message.video.file_id)
            filename = "video.mp4"
        elif message.audio:
            file_info = await bot.get_file(message.audio.file_id)
            filename = "audio.mp3"

        file_path = f"/tmp/{filename}"
        await bot.download_file(file_info.file_path, file_path)

        transcript, summary = await process_audio_or_video(file_path)
        formatted = format_transcript(transcript)

        pdf = generate_pdf(formatted, summary)
        md = generate_markdown(formatted, summary)

        await message.answer_document(FSInputFile(pdf))
        await message.answer_document(FSInputFile(md))

        os.remove(file_path)
        os.remove(pdf)
        os.remove(md)

    await enqueue(message, task())


# -------------------------------
#   Приём ссылок
# -------------------------------
@dp.message(lambda m: m.text and ("http" in m.text))
async def handle_link(message: types.Message):

    await message.answer("🔗 Скачиваю файл по ссылке...")

    async def task():
        file_path = await download_from_link(message.text, message)

        if not file_path:
            await message.answer("❌ Не удалось скачать файл")
            return

        transcript, summary = await process_audio_or_video(file_path)
        formatted = format_transcript(transcript)

        pdf = generate_pdf(formatted, summary)
        md = generate_markdown(formatted, summary)

        await message.answer_document(FSInputFile(pdf))
        await message.answer_document(FSInputFile(md))

        os.remove(file_path)
        os.remove(pdf)
        os.remove(md)

    await enqueue(message, task())


# -------------------------------
#   Запуск
# -------------------------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
