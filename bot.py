import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile
from dotenv import load_dotenv

from link_downloader import (
    is_direct_link,
    is_social_link,
    is_youtube_link,
    download_any,
)

from file_generators import generate_pdf, generate_markdown
from formatter import format_transcript
from transcriber import process_audio_or_video


# ----------------- Очередь задач -----------------
queue = asyncio.Queue()
processing = False


async def worker():
    """
    Фоновый обработчик задач.
    Позволяет обрабатывать запросы последовательно.
    """
    global processing
    processing = True

    while True:
        message = await queue.get()
        try:
            await handle_task(message)
        except Exception as e:
            await message.answer(f"❌ Ошибка обработки: {e}")
        finally:
            queue.task_done()


# ----------------- Основная логика -----------------

async def handle_task(message: types.Message):
    """
    Обработчик одной задачи (аудио, видео, ссылки).
    """

    # ---------- Видео / аудио файл ----------
    if message.video or message.audio or message.document:
        file_id = (
            message.video.file_id
            if message.video
            else message.audio.file_id
            if message.audio
            else message.document.file_id
        )

        file = await message.bot.get_file(file_id)
        file_path = f"downloads/{file.file_unique_id}.mp4"
        os.makedirs("downloads", exist_ok=True)

        await message.answer("⬇️ Скачиваю файл...")

        await message.bot.download_file(file.file_path, file_path)

        await message.answer("🎧 Обрабатываю аудио/видео...")

        transcript, summary = await process_audio_or_video(file_path)

        formatted_text = format_transcript(transcript)

        pdf_path = generate_pdf(formatted_text, summary)
        md_path = generate_markdown(formatted_text, summary)

        await message.answer("📄 Отправляю файлы...")

        await message.answer_document(FSInputFile(pdf_path))
        await message.answer_document(FSInputFile(md_path))
        return

    # ---------- Ссылка ----------
    if message.text:
        url = message.text.strip()

        await message.answer("🔗 Обнаружена ссылка. Проверяю...")

        if not (
            is_direct_link(url)
            or is_social_link(url)
            or is_youtube_link(url)
        ):
            await message.answer("❌ Неподдерживаемая ссылка.")
            return

        await message.answer("⬇️ Скачиваю файл по ссылке...")

        downloaded_file = await download_any(url)

        await message.answer("🎧 Обрабатываю контент...")

        transcript, summary = await process_audio_or_video(downloaded_file)

        formatted_text = format_transcript(transcript)

        pdf_path = generate_pdf(formatted_text, summary)
        md_path = generate_markdown(formatted_text, summary)

        await message.answer_document(FSInputFile(pdf_path))
        await message.answer_document(FSInputFile(md_path))
        return

    await message.answer("❌ Не могу обработать ваш запрос.")


# ----------------- Aiogram BOT -----------------

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.answer(
        "👋 Привет! Отправь видео, аудио или ссылку — я всё обработаю и сделаю текст + PDF."
    )


@dp.message()
async def on_message(message: types.Message):
    """
    Вместо обработки — кладём задачу в очередь.
    """
    await message.answer("⏳ Задача поставлена в очередь. Ожидайте...")
    await queue.put(message)


# ----------------- MAIN -----------------

async def main():
    asyncio.create_task(worker())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
