import os
import uuid
import requests
import yt_dlp


# ---------------------------------------------------------
# Универсальный загрузчик видео по ссылке
# ---------------------------------------------------------
async def download_video_from_url(url: str) -> str:
    os.makedirs("downloads", exist_ok=True)
    filename = f"downloads/{uuid.uuid4()}.mp4"

    # 1) YouTube, Vimeo, соцсети — через yt-dlp
    if "youtube.com" in url or "youtu.be" in url or "vimeo.com" in url:
        ydl_opts = {
            "outtmpl": filename,
            "format": "mp4/bestvideo+bestaudio/best"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return filename

    # 2) Google Drive (прямая ссылка на файл)
    if "drive.google.com" in url:
        file_id = _extract_drive_id(url)
        if file_id:
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            return _download_direct(download_url, filename)

    # 3) Dropbox → превращаем dl=0 в dl=1
    if "dropbox.com" in url:
        if "?dl=0" in url:
            url = url.replace("?dl=0", "?dl=1")
        return _download_direct(url, filename)

    # 4) Яндекс.Диск (API качает прямую ссылку)
    if "yadi.sk" in url or "disk.yandex" in url:
        api_url = "https://cloud-api.yandex.net/v1/disk/public/resources/download"
        resp = requests.get(api_url, params={"public_key": url}).json()
        return _download_direct(resp.get("href"), filename)

    # 5) Прямые ссылки (mp4, mov, avi)
    if url.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
        return _download_direct(url, filename)

    # fallback
    return _download_direct(url, filename)


# ---------------------------------------------------------
# Google Drive — получение ID
# ---------------------------------------------------------
def _extract_drive_id(url: str):
    if "id=" in url:
        return url.split("id=")[1].split("&")[0]
    if "/d/" in url:
        return url.split("/d/")[1].split("/")[0]
    return None


# ---------------------------------------------------------
# Прямое скачивание файла
# ---------------------------------------------------------
def _download_direct(url: str, filename: str) -> str:
    r = requests.get(url, stream=True)
    r.raise_for_status()

    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    return filename
