import os
import asyncio
import logging

from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Update

import redis.asyncio as aioredis

from config import BOT_TOKEN, REDIS_URL, WEBHOOK_SECRET
from worker_queue import enqueue_task


# -------------------------------------------------
# LOGGING
# -------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="SERVER | %(asctime)s | %(levelname)s | %(message)s"
)

# -------------------------------------------------
# Initialize
# -------------------------------------------------
app = FastAPI()
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)


# -------------------------------------------------
# Webhook endpoint
# -------------------------------------------------
@app.post("/webhook")
async def telegram_webhook(request: Request):

    # 1) Telegram always sends a secret header
    incoming_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if incoming_secret != WEBHOOK_SECRET:
        logging.warning("❌ WRONG SECRET TOKEN IN WEBHOOK")
        return {"status": "forbidden"}

    body = await request.json()

    update = Update(**body)

    # Тут мы НЕ обрабатываем сами апдейты.
    # Вместо этого все задачи отправляем в очередь Redis.
    asyncio.create_task(enqueue_task(redis_client, update.model_dump_json()))

    return {"ok": True}


# -------------------------------------------------
# Root for checking server
# -------------------------------------------------
@app.get("/")
async def home():
    return {"status": "running", "bot": "Скриптор AI"}


# -------------------------------------------------
# Webhook registration (only once)
# -------------------------------------------------
@app.on_event("startup")
async def on_startup():
    webhook_url = os.getenv("WEBHOOK_URL")

    logging.info(f"Setting webhook → {webhook_url}")

    # удаляем предыдущие Webhook'и
    await bot.delete_webhook(drop_pending_updates=True)

    await bot.set_webhook(
        url=webhook_url,
        secret_token=WEBHOOK_SECRET,
        max_connections=100
    )

    logging.info("Webhook successfully set ✔")


# -------------------------------------------------
# Remove webhook on shutdown
# -------------------------------------------------
@app.on_event("shutdown")
async def on_shutdown():
    logging.info("Removing webhook…")
    await bot.delete_webhook()
