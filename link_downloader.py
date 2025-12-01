import os
import yt_dlp
import aiohttp
import asyncio
from typing import Optional, Callable

CHUNK_SIZE = 1024 * 512  # 512 KB


async def download_file(url: str, dest_path: str, progress_callback: Optional[Callable] = None):
    """
    Download direct file URL with progress updates.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0

            with open(dest_path, "wb") as f:
                async for chunk in resp.content.iter_chunked(CHUNK_SIZE):
                    f.write(chunk)
                    downloaded += len(chunk)

                    if progress_callback and total > 0:
                        await progress_callback(int(downloaded / total * 100))

    return dest_path


async def download_youtube(url: str, dest_path: str, progress_callback: Optional[Callable] = None):
    """
    Download YouTube video using yt-dlp with progress callback.
    """
    loop = asyncio.get_event_loop()

    def hook(d):
        if d.get("status") == "downloading":
            if progress_callback:
                percent_raw = d.get("_percent_str", "0%").replace("%", "")
                try:
                    percent = int(float(percent_raw))
                    loop.create_task(progress_callback(percent))
                except:
                    pass

    ydl_opts = {
        "outtmpl": dest_path,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "progress_hooks": [hook],
        "noprogress": True,
        "nocheckcertificate": True,
    }

    def run():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    await asyncio.to_thread(run)
    return dest_path


async def download_social(url: str, dest_path: str, progress_callback: Optional[Callable] = None):
    """
    Download Instagram, TikTok, Facebook using yt-dlp.
    """
    return await download_youtube(url, dest_path, progress_callback)


async def smart_download(url: str, dest_path: str, progress_callback: Optional[Callable] = None):
    """
    Smart downloader detects source automatically.
    """
    url_lower = url.lower()

    try:
        if "youtube.com" in url_lower or "youtu.be" in url_lower:
            return await download_youtube(url, dest_path, progress_callback)

        if any(s in url_lower for s in ["tiktok.com", "instagram.com", "facebook.com"]):
            return await download_social(url, dest_path, progress_callback)

        return await download_file(url, dest_path, progress_callback)

    except Exception as e:
        raise RuntimeError(f"Download failed: {str(e)}")
