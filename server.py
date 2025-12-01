from fastapi import FastAPI, Request
from aiogram import Bot
from worker_queue import enqueue_task
from config import TELEGRAM_TOKEN, WEBHOOK_SECRET, WEBHOOK_URL
import hashlib

bot = Bot(token=TELEGRAM_TOKEN)

app = FastAPI()


def verify_secret(request: Request):
    header = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    return header == WEBHOOK_SECRET


@app.post("/webhook")
async def webhook(request: Request):
    if not verify_secret(request):
        return {"status": "forbidden"}

    update = await request.json()

    # только ссылки на скачивание
    if "message" in update and "text" in update["message"]:
        url = update["message"]["text"]
        chat_id = update["message"]["chat"]["id"]

        await enqueue_task({"chat_id": chat_id, "url": url})

    return {"status": "ok"}


@app.get("/")
async def root():
    return {"status": "running"}
