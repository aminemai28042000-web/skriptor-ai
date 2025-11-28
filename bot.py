import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

from utils.link_downloader import download_video_from_url
from utils.transcriber import transcribe_audio
from utils.file_generators import generate_pdf, generate_markdown
from utils.formatter import format_transcript

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


# ===========================
# /start
# ===========================
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "<b>👋 Привет! Я — Скриптор AI.</b>\n\n"
        "Загрузи видео или отправь ссылку, и я сделаю для тебя:\n"
        "• Полную транскрибацию\n"
        "• Структурированную PDF\n"
        "• Markdown-конспект\n\n"
        "Видео можно отправлять до 2 ГБ.\n"
        "Ссылки — без ограничений."
    )


# ===========================
# обработка ссылки
# ===========================
@dp.message(F.text.startswith("http"))
async def handle_url(message: Message):
    url = message.text.strip()
    status = await message.answer("⏳ Загружаю видео по ссылке...")

    try:
        filepath = await download_video_from_url(url)
        await status.edit_text("🎬 Видео скачано. Начинаю распознавание...")
    except Exception as e:
        await status.edit_text("❌ Ошибка при загрузке видео.")
        return

    await process_video(message, filepath, status)


# ===========================
# обработка загруженного видео
# ===========================
@dp.message(F.video | F.document)
async def handle_video(message: Message):
    status = await message.answer("⏳ Загружаю файл...")

    file = message.video or message.document
    file_info = await bot.get_file(file.file_id)

    filepath = f"downloads/{file.file_id}.mp4"
    os.makedirs("downloads", exist_ok=True)

    await bot.download_file(file_info.file_path, filepath)
    await status.edit_text("🎬 Видео загружено. Начинаю распознавание...")

    await process_video(message, filepath, status)


# ===========================
# общий процесс обработки видео
# ===========================
async def process_video(message: Message, filepath: str, status_msg: Message):
    try:
        text = await transcribe_audio(filepath)

        await status_msg.edit_text("📝 Форматирую текст...")
        clean_text = format_transcript(text)

        await status_msg.edit_text("📄 Генерирую файлы...")

        pdf_path = generate_pdf(clean_text)
        md_path = generate_markdown(clean_text)

        await status_msg.edit_text("✅ Готово! Файлы готовы к скачиванию.")

        await message.answer_document(document=open(pdf_path, "rb"))
        await message.answer_document(document=open(md_path, "rb"))

    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка при обработке: {e}")

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


# ===========================
# запуск
# ===========================
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
