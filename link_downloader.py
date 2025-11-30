import os
import asyncio
import yt_dlp
import aiohttp

# -----------------------------
#   Прогресс YouTube
# -----------------------------
def progress_hook(message):
    if message['status'] == 'downloading':
        percent = message.get("_percent_str", "0%")
        asyncio.create_task(message['ctx'].edit_text(f"⬇ Скачивание: {percent}"))
    elif message['status'] == 'finished':
        asyncio.create_task(message['ctx'].edit_text("⏳ Завершаю..."))


# -----------------------------
#   Скачивание YouTube/TikTok/Instagram
# -----------------------------
async def download_yt(url, message):
    loop = asyncio.get_running_loop()

    out = f"/tmp/{os.urandom(8).hex()}.mp4"

    def _run():
        ydl_opts = {
            "outtmpl": out,
            "format": "mp4",
            "progress_hooks": [progress_hook],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl._ctx = message
            ydl.download([url])
        return out

    return await loop.run_in_executor(None, _run)


# -----------------------------
#   Прямой URL (mp3/mp4/webm)
# -----------------------------
async def download_direct(url, message):
    filename = f"/tmp/{os.urandom(8).hex()}"
    ext = url.split("?")[0].split(".")[-1]
    filename += f".{ext}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None

            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            chunk = 1024 * 1024

            with open(filename, "wb") as f:
                async for part in resp.content.iter_chunked(chunk):
                    f.write(part)
                    downloaded += len(part)
                    if total:
                        percent = f"{(downloaded / total) * 100:.1f}%"
                        await message.edit_text(f"⬇ Загружаю: {percent}")

    return filename


# -----------------------------
#   Главная функция
# -----------------------------
async def download_from_link(url: str, message):

    # YouTube / TikTok / Instagram
    if any(x in url for x in ["youtube.com", "youtu.be", "tiktok.com", "instagram.com", "reels"]):
        return await download_yt(url, message)

    # прямой файл
    return await download_direct(url, message)
