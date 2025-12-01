import os
import asyncio
from aiohttp import web
import aiohttp
from config import BOT_TOKEN, WORKER_URL
from utils import send_progress_message, is_youtube_url
from link_downloader import download_from_link
from transcriber import process_file

# Telegram API URL
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

routes = web.RouteTableDef()

# ------------------------------------
#  Helper: send message to Telegram
# ------------------------------------
async def tg_send(chat_id, text, reply_to=None):
    async with aiohttp.ClientSession() as session:
        await session.post(
            f"{TG_API}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "reply_to_message_id": reply_to
            }
        )


# ------------------------------------
#  Webhook entrypoint
# ------------------------------------
@routes.post("/webhook")
async def webhook(request):
    update = await request.json()

    if "message" not in update:
        return web.Response(text="OK")

    msg = update["message"]
    chat_id = msg["chat"]["id"]

    # TEXT or LINK
    if "text" in msg:
        text = msg["text"]

        if is_youtube_url(text):
            task = {
                "chat_id": chat_id,
                "source": "youtube",
                "url": text
            }
            await queue_task(task)
            await tg_send(chat_id, "🎬 Получена ссылка. Начинаю скачивание...")
            return web.Response(text="OK")

        await tg_send(chat_id, "Отправьте ссылку или видеофайл.")
        return web.Response(text="OK")

    # FILE (video/audio/document)
    file_id = None
    if "video" in msg:
        file_id = msg["video"]["file_id"]
    elif "document" in msg:
        file_id = msg["document"]["file_id"]
    elif "audio" in msg:
        file_id = msg["audio"]["file_id"]

    if file_id:
        task = {
            "chat_id": chat_id,
            "source": "tg_file",
            "file_id": file_id
        }
        await queue_task(task)
        await tg_send(chat_id, "📥 Файл получен. Ставлю в очередь...")
        return web.Response(text="OK")

    return web.Response(text="OK")


# ------------------------------------
#   Send task to worker
# ------------------------------------
async def queue_task(task: dict):
    async with aiohttp.ClientSession() as session:
        await session.post(f"{WORKER_URL}/queue", json=task)


# ------------------------------------
#  Server start
# ------------------------------------
def run():
    app = web.Application(client_max_size=2 * 1024 ** 3)  # 2GB
    app.add_routes(routes)
    web.run_app(app, port=8000)


if __name__ == "__main__":
    run()
