import asyncio
from fastapi import FastAPI, Request
from aiogram import Bot
import aiohttp
from worker_queue import enqueue_task
from config import TELEGRAM_TOKEN, WEBHOOK_SECRET, WEBHOOK_URL

bot = Bot(token=TELEGRAM_TOKEN)
app = FastAPI()


def verify_secret(request: Request):
    header = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    return header == WEBHOOK_SECRET


@app.on_event("startup")
async def on_startup():
    """
    Устанавливаем вебхук при запуске контейнера.
    """
    async with aiohttp.ClientSession() as session:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"

        payload = {
            "url": WEBHOOK_URL,
            "secret_token": WEBHOOK_SECRET
        }

        async with session.post(url, data=payload) as resp:
            data = await resp.text()
            print("WEBHOOK SET RESPONSE:", data)


@app.post("/webhook")
async def webhook(request: Request):
    if not verify_secret(request):
        return {"status": "forbidden"}

    update = await request.json()

    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        url = update["message"]["text"]

        await enqueue_task({"chat_id": chat_id, "url": url})

    return {"status": "ok"}


@app.get("/")
async def root():
    return {"status": "running"}
