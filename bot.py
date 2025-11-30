import os
import time
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
import yt_dlp

from file_generators import generate_pdf, generate_markdown
from transcriber import process_audio_or_video
from formatter import format_transcript
from link_downloader import is_direct_link
from link_downloader import normalize_url
from link_downloader import get_filename_from_url
from formatter import log_event

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Очередь обработки задач
task_queue = asyncio.Queue()

# ================ ПРОГРЕСС ==================

async def update_progress(message, percent):
    """Обновление текста прогресса."""
    percent = str(percent).replace("%", "")
    try:
        await message.edit_text(f"⬇️ Скачивание… {percent}%")
    except:
        pass


# ================ ОБРАБОТКА РУССКИЙ КОНТЕНТ ==================

async def process_and_reply(message: Message, file_path: str):
    """Обработка видео/аудио → транскрипт → PDF/MD."""
    try:
        transcript, summary = await process_audio_or_video(file_path)

        if not transcript:
            await message.reply("❌ Ошибка обработки. Попробуйте другое видео.")
            return

        formatted = format_transcript(transcript)

        pdf_path = generate_pdf(formatted, summary)
        md_path = generate_markdown(formatted, summary)

        await message.reply_document(open(pdf_path, "rb"))
        await message.reply_document(open(md_path, "rb"))

        log_event(message.from_user.id, "complete", "Success")

        # Удаление временных файлов
        try:
            os.remove(file_path)
            os.remove(pdf_path)
            os.remove(md_path)
        except:
            pass

    except Exception as e:
        await message.reply(f"⚠️ Ошибка обработки файла: {e}")


# ================ АСИНХРОННЫЙ РАБОЧИЙ ПОТОК ==================

async def worker():
    """Очередь задач, чтобы бот не падал при нагрузке."""
    while True:
        message, file_path = await task_queue.get()
        try:
            await process_and_reply(message, file_path)
        except Exception as e:
            await message.reply(f"⚠️ Ошибка: {e}")
        finally:
            task_queue.task_done()


# ================ СКАЧИВАНИЕ ЧЕРЕЗ TELEGRAM (до 2 ГБ) ==================

async def download_from_telegram(message: Message, file_obj):
    tg_file = await bot.get_file(file_obj.file_id)
    url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{tg_file.file_path}"

    os.makedirs("downloads", exist_ok=True)
    file_path = f"downloads/{file_obj.file_unique_id}"

    progress_msg = await message.reply("⬇️ Скачивание… 0%")

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0

            with open(file_path, "wb") as f:
                async for chunk in resp.content.iter_chunked(1024 * 1024):
                    f.write(chunk)
                    downloaded += len(chunk)

                    if total > 0:
                        percent = int(downloaded * 100 / total)
                        await update_progress(progress_msg, percent)

    await progress_msg.edit_text("✨ Скачивание завершено! Обрабатываю файл…")
    return file_path


# ================ СКАЧИВАНИЕ ПРЯМЫХ HTTPS-ССЫЛОК ==================

async def download_direct(url: str, message: Message, filename=None):
    os.makedirs("downloads", exist_ok=True)

    if not filename:
        filename = get_filename_from_url(url)

    file_path = os.path.join("downloads", filename)

    progress_msg = await message.reply("⬇️ Скачивание… 0%")

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0

            with open(file_path, "wb") as f:
                async for chunk in resp.content.iter_chunked(1024 * 1024):
                    f.write(chunk)
                    downloaded += len(chunk)

                    if total > 0:
                        percent = int(downloaded * 100 / total)
                        await update_progress(progress_msg, percent)

    await progress_msg.edit_text("✨ Файл скачан! Обрабатываю…")
    return file_path


# ================ СКАЧИВАНИЕ YOUTUBE / INSTAGRAM / TIKTOK / TWITTER ==================

async def download_social(url: str, message: Message):
    os.makedirs("downloads", exist_ok=True)
    base = f"downloads/{message.from_user.id}_{int(time.time())}"
    file_path = base + ".mp4"

    progress_msg = await message.reply("⬇️ Скачивание… 0%")

    # hook для прогресса
    def hook(d):
        if d["status"] == "downloading":
            percent = d.get("_percent_str", "0%").replace("%", "")
            asyncio.create_task(update_progress(progress_msg, percent))

    ydl_opts = {
        "outtmpl": file_path,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "noprogress": True,
        "progress_hooks": [hook],
        "quiet": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        await message.reply(f"❌ Ошибка загрузки видео: {e}")
        return None

    await progress_msg.edit_text("✨ Видео скачано! Обрабатываю…")
    return file_path


# ================ ОБРАБОТЧИК СОЦСЕТЕЙ, HTTPS И ТЕЛЕГРАМА ==================

@dp.message(F.text & ~F.is_command())
async def handle_text(message: Message):
    url = message.text.strip()

    if not url.startswith(("http://", "https://")):
        return

    # нормализация Google Drive, Dropbox, Mega …
    url = normalize_url(url)

    # 1 — прямой https
    if is_direct_link(url):
        file = await download_direct(url, message)
        await task_queue.put((message, file))
        return

    # 2 — YouTube/TikTok/Instagram и др.
    if any(x in url for x in [
        "youtube.com", "youtu.be",
        "tiktok.com", "instagram.com",
        "twitter.com", "x.com",
        "facebook.com", "fb.watch",
        "vimeo.com", "rutube.ru"
    ]):
        file = await download_social(url, message)
        if file:
            await task_queue.put((message, file))
        return

    await message.reply("❌ Не удалось распознать ссылку.")


# ================ ТЕЛЕГРАМ ВИДЕО/АУДИО/ФАЙЛЫ ==================

@dp.message(F.video | F.audio | F.document)
async def handle_media(message: Message):
    file_obj = message.document or message.video or message.audio

    file_path = await download_from_telegram(message, file_obj)
    await task_queue.put((message, file_path))


# ================ СТАРТ ==================

@dp.message(F.text == "/start")
async def start_cmd(message: Message):
    await message.reply(
        "🎧 *Скриптор AI* готов к работе!\n\n"
        "Отправьте:\n"
        "• видео / аудио / файл (до 2 ГБ)\n"
        "• ссылку на YouTube, TikTok, Instagram, X/Twitter\n"
        "• прямую HTTPS ссылку\n\n"
        "И получите:\n"
        "• транскрипт\n"
        "• PDF\n"
        "• Markdown файл\n",
        parse_mode=ParseMode.MARKDOWN
    )


# ================ ЗАПУСК ==================

async def main():
    asyncio.create_task(worker())  # очередь задач
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
