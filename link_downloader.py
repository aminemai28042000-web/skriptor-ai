import os
import aiohttp
import asyncio
from pathlib import Path
from functools import partial

# -------------------------------------------------
# Простая загрузка обычных файлов
# -------------------------------------------------
async def download_file(url: str, dest_path: str, progress_callback=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()

            total = response.content_length or 0
            downloaded = 0

            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            with open(dest_path, "wb") as f:
                async for chunk in response.content.iter_chunked(1024 * 64):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        await progress_callback(downloaded, total)

    return dest_path


# -------------------------------------------------
# Заглушки под YouTube / TikTok / Instagram / Facebook
# Здесь должна быть твоя реальная логика скачивания.
# -------------------------------------------------

async def download_youtube(url: str, dest_path: str, progress_callback=None):
    # ❗ Тут можно подключить yt-dlp
    return await download_file(url, dest_path, progress_callback)


async def download_social(url: str, dest_path: str, progress_callback=None):
    return await download_file(url, dest_path, progress_callback)


# -------------------------------------------------
# Умная функция выбора источника (YouTube, соцсети, файл)
# -------------------------------------------------
async def smart_download(url: str, dest_path: str, progress_callback=None):
    url_lower = url.lower()

    try:
        # YouTube
        if "youtube.com" in url_lower or "youtu.be" in url_lower:
            return await download_youtube(url, dest_path, progress_callback)

        # TikTok / Instagram / Facebook
        if any(s in url_lower for s in ["tiktok.com", "instagram.com", "facebook.com"]):
            return await download_social(url, dest_path, progress_callback)

        # Обычный файл
        return await download_file(url, dest_path, progress_callback)

    except Exception as e:
        raise RuntimeError(f"Download failed: {str(e)}")


# -------------------------------------------------
# Важная функция!
# Её вызывает worker.py
# -------------------------------------------------
async def download_file_with_progress(
    url: str,
    dest_path: str,
    progress_callback=None
):
    return await smart_download(url, dest_path, progress_callback)
