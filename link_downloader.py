import os
import re
import uuid
import yt_dlp
import aiohttp
import asyncio

# --- Проверяем тип ссылки ---
def is_youtube_link(url: str) -> bool:
    return "youtube.com" in url or "youtu.be" in url

def is_social_link(url: str) -> bool:
    SOCIAL_PATTERNS = [
        "tiktok.com",
        "instagram.com",
        "vk.com",
        "twitter.com",
        "x.com",
        "facebook.com",
        "fb.watch",
        "reddit.com",
    ]
    return any(p in url for p in SOCIAL_PATTERNS)

def is_direct_link(url: str) -> bool:
    return url.lower().startswith(("http://", "https://")) and url.split("?")[0].split("/")[-1].count(".") >= 1


# --- Скачать напрямую ---
async def download_direct(url: str, folder="downloads"):
    os.makedirs(folder, exist_ok=True)
    filename = url.split("/")[-1].split("?")[0]
    filepath = os.path.join(folder, filename)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception("Ошибка скачивания: статус", resp.status)

            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0

            with open(filepath, "wb") as f:
                async for chunk in resp.content.iter_chunked(1024 * 256):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        progress = int(downloaded / total * 100)
                        print(f"⏳ Прогресс: {progress}%")

    return filepath


# --- Скачать соцсети / YouTube через yt-dlp ---
async def download_with_ytdlp(url: str, folder="downloads"):
    os.makedirs(folder, exist_ok=True)
    filename = f"{uuid.uuid4()}.mp4"
    filepath = os.path.join(folder, filename)

    ydl_opts = {
        "outtmpl": filepath,
        "format": "bestvideo+bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4",
    }

    def run():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, run)

    return filepath


# --- Универсальная функция ---
async def download_any(url: str):
    if is_direct_link(url):
        return await download_direct(url)

    if is_youtube_link(url) or is_social_link(url):
        return await download_with_ytdlp(url)

    raise Exception("⛔ Неподдерживаемая ссылка")
