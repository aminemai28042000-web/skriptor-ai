import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode

from link_downloader import download_video_by_link
from transcriber import process_audio_or_video
from file_generators import generate_pdf, generate_markdown
from formatter import format_transcript
from utils.rate_limiter import is_rate_limited
from utils.csv_logger import log_event

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


# ---------- ОБРАБОТКА СООБЩЕНИЙ ---------- #

@dp.message(F.text)
async def handle_text(message: Message):
    text = message.text.strip()

    # Анти-спам (лимит 1 запрос / 30 сек)
    if is_rate_limited(message.from_user.id):
        await message.reply("⚠️ Подождите немного перед следующим запросом.")
        return

    log_event(message.from_user.id, "text_input", text)

    # Если ссылка — скачиваем
    if (
        "http://"
        in text
        or "https://"
        in text
        or "youtu.be" in text
        or "youtube.com" in text
    ):
        await message.reply("🔄 Скачиваю видео по ссылке…")

        file_path = await download_video_by_link(text)

        if not file_path:
            await message.reply("❌ Не удалось скачать это видео. Попробуйте другое.")
            return

        await handle_file(message, file_path)
        return

    await message.reply(
        "Отправьте видео/аудио или ссылку для транскрибации 🎧"
    )


@dp.message(F.video | F.audio | F.document)
async def handle_media(message: Message):
    # Анти-спам
    if is_rate_limited(message.from_user.id):
        await message.reply("⚠️ Подождите немного перед следующим запросом.")
        return

    log_event(message.from_user.id, "file_input", "Media Upload")

    file = await message.bot.get_file(message.document.file_id if message.document else (message.video.file_id if message.video else message.audio.file_id))
    file_path = f"downloads/{file.file_unique_id}"

    await bot.download_file(file.file_path, file_path)

    await handle_file(message, file_path)


# ---------- ОСНОВНАЯ ОБРАБОТКА ФАЙЛОВ ---------- #

async def handle_file(message: Message, file_path: str):
    await message.reply("🎙️ Обрабатываю файл…")

    transcript, summary = await process_audio_or_video(file_path)

    if not transcript:
        await message.reply("❌ Ошибка обработки. Попробуйте другое видео.")
        return

    formatted_transcript = format_transcript(transcript)

    # Генерация файлов
    pdf_path = generate_pdf(formatted_transcript, summary)
    md_path = generate_markdown(formatted_transcript, summary)

    await message.reply("📄 Готово! Отправляю файлы…")

    # Отправка пользователю
    await message.reply_document(open(pdf_path, "rb"))
    await message.reply_document(open(md_path, "rb"))

    # Чистим мусор
    try:
        os.remove(file_path)
        os.remove(pdf_path)
        os.remove(md_path)
    except:
        pass

    log_event(message.from_user.id, "complete", "Success")


# ---------- ЗАПУСК БОТА ---------- #

async def main():
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
