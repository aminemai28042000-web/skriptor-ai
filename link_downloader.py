import os
import uuid
import asyncio
import yt_dlp


DOWNLOAD_DIR = "downloads"

# создаём папку, если нет
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


async def download_video_by_link(url: str) -> str:
    """
    Скачивает видео по ссылке (YouTube / прямые ссылки / соцсети)
    Возвращает путь к локальному файлу или None при ошибке
    """

    temp_name = str(uuid.uuid4()) + ".mp4"
    output_path = os.path.join(DOWNLOAD_DIR, temp_name)

    ydl_opts = {
        "outtmpl": output_path,
        "format": "bestvideo+bestaudio/best",
        "retries": 3,
        "quiet": True,
        "noprogress": True,
        "merge_output_format": "mp4",
    }

    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, lambda: _download_sync(url, ydl_opts))
        return output_path

    except Exception as e:
        print("DOWNLOAD ERROR:", e)
        return None


def _download_sync(url, options):
    """Синхронная часть yt-dlp — выносится в executor"""
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])
