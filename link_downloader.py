import os
import re
import asyncio
import yt_dlp
import aiohttp

# -------------------- Проверка типов ссылок --------------------

def is_youtube_link(url: str) -> bool:
    return "youtube.com" in url or "youtu.be" in url

def is_social_link(url: str) -> bool:
    return any(s in url for s in [
        "instagram.com", "tiktok.com", "vm.tiktok.com",
        "facebook.com", "twitter.com", "x.com",
        "vk.com", "rutube.ru"
    ])

def is_direct_link(url: str) -> bool:
    return url.lower().endswith((
        ".mp4", ".mov", ".avi", ".mkv",
        ".mp3", ".wav", ".m4a", ".aac"
    ))

# -------------------- Прогресс-бар YT-DLP --------------------

class ProgressHook:
    def __init__(self, callback):
        self.callback = callback

    async def __call__(self, d):
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)

            if total:
                percent = int(downloaded / total * 100)
                await self.callback(percent)

# -------------------- Скачивание YouTube / соцсетей --------------------

async def download_yt(url: str, on_progress=None) -> str:
    os.makedirs("downloads", exist_ok=True)
    out_path = "downloads/%(id)s.%(ext)s"

    loop = asyncio.get_running_loop()

    hook = ProgressHook(on_progress) if on_progress else None

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": out_path,
        "merge_output_format": "mp4",
        "progress_hooks": [hook] if hook else [],
        "noplaylist": True,
    }

    def extract():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)

    file_path = await loop.run_in_executor(None, extract)
    return file_path

# -------------------- Прямое скачивание больших файлов --------------------

async def download_direct(url: str, on_progress=None) -> str:
    os.makedirs("downloads", exist_ok=True)
    filename = "downloads/" + os.path.basename(url.split("?")[0])

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0

            with open(filename, "wb") as f:
                async for chunk in resp.content.iter_chunked(1024 * 512):
                    f.write(chunk)
                    downloaded += len(chunk)

                    if total and on_progress:
                        percent = int(downloaded / total * 100)
                        await on_progress(percent)

    return filename

# -------------------- Универсальное скачивание --------------------

async def download_any(url: str, on_progress=None) -> str:

    if is_youtube_link(url) or is_social_link(url):
        return await download_yt(url, on_progress)

    if is_direct_link(url):
        return await download_direct(url, on_progress)

    raise ValueError("Неподдерживаемая ссылка")
