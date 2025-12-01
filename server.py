import aiohttp
from fastapi import FastAPI, Request
from aiogram import Bot
from worker_queue import enqueue_task
from config import TELEGRAM_TOKEN, WEBHOOK_SECRET, WEBHOOK_URL

bot = Bot(token=TELEGRAM_TOKEN)
app = FastAPI()


def verify_secret(request: Request):
    header = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    return header == WEBHOOK_SECRET


@app.on_event("startup")
async def startup():
    async with aiohttp.ClientSession() as session:
        payload = {
            "url": WEBHOOK_URL,
            "secret_token": WEBHOOK_SECRET
        }

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
        async with session.post(url, data=payload) as resp:
            print("Webhook response:", await resp.text())


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
