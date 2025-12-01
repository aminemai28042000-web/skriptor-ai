import os
import re
import aiohttp
import asyncio
import logging
import tempfile
from aiogram import Bot

from config import BOT_TOKEN

# Bot instance (needed for progress updates)
bot = Bot(token=BOT_TOKEN)

# ---------------------------------------------------------
# Extract filename from URL
# ---------------------------------------------------------
def get_filename_from_url(url: str) -> str:
    try:
        name = url.split("/")[-1].split("?")[0]
        if len(name) < 3:
            return "downloaded_file"
        return name
    except:
        return "downloaded_file"


# ---------------------------------------------------------
# Send progress to Telegram
# ---------------------------------------------------------
async def send_progress(chat_id: int, pct: float):
    try:
        await bot.send_message(chat_id, f"⏳ Прогресс загрузки: {pct:.0f}%")
    except:
        pass


# ---------------------------------------------------------
# YouTube/TikTok/Instagram direct extractor (basic)
# — In full future version we’ll expand this.
# ---------------------------------------------------------
async def maybe_extract_real_url(url: str) -> str:
    """
    Простой предобработчик: если ссылка на соцсети — пользователь обычно
    присылает страницу, а не прямой файл. Вернём как есть — скачивание всё
    равно будет attempt-иться.
    Позже сюда можно встроить pytube/tiktok-scraper и т.д.
    """
    return url


# ---------------------------------------------------------
# Streaming download (with progress)
# ---------------------------------------------------------
async def download_file_with_progress(
    bot: Bot, chat_id: int, url: str
) -> str | None:

    logging.info(f"⬇ Начинаю скачивание: {url}")

    # Try extract real media link (YouTube/TikTok/etc)
    url = await maybe_extract_real_url(url)

    # temp directory
    temp_dir = tempfile.gettempdir()
    filename = get_filename_from_url(url)
    temp_path = os.path.join(temp_dir, filename)

    # Request + stream
    try:
        timeout = aiohttp.ClientTimeout(total=None)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:

                if resp.status != 200:
                    logging.error(f"❌ HTTP {resp.status}")
                    return None

                total = resp.headers.get("Content-Length")
                total = int(total) if total else None
                downloaded = 0
                last_pct_update = 0

                with open(temp_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(1024 * 1024):
                        if not chunk:
                            continue

                        f.write(chunk)
                        downloaded += len(chunk)

                        # progress calculation
                        if total:
                            pct = downloaded / total * 100
                            # update every 5%
                            if pct - last_pct_update >= 5:
                                last_pct_update = pct
                                await send_progress(chat_id, pct)

        logging.info(f"✔ Файл скачан: {temp_path}")
        return temp_path

    except Exception as e:
        logging.error(f"❌ Ошибка скачивания: {e}")
        return None
