import os
import json
import asyncio
import logging
import traceback
import redis.asyncio as aioredis

from aiogram import Bot
from aiogram.types import FSInputFile

from config import BOT_TOKEN, REDIS_URL
from link_downloader import download_file_with_progress
from transcriber import process_audio_or_video

bot = Bot(token=BOT_TOKEN)

async def process_task(task_json: str):
    try:
        data = json.loads(task_json)
        chat_id = data["message"]["chat"]["id"]

        # determine input type
        if "text" in data["message"]:
            url = data["message"]["text"].strip()
            file_path = await download_file_with_progress(bot, chat_id, url)
        elif "document" in data["message"]:
            file_id = data["message"]["document"]["file_id"]
            file = await bot.get_file(file_id)
            file_path = f"/tmp/{data['message']['document']['file_name']}"
            await bot.download_file(file.file_path, file_path)
        elif "video" in data["message"]:
            file_id = data["message"]["video"]["file_id"]
            file = await bot.get_file(file_id)
            file_path = f"/tmp/video.mp4"
            await bot.download_file(file.file_path, file_path)
        else:
            await bot.send_message(chat_id, "Не удалось определить тип сообщения.")
            return

        if not file_path:
            await bot.send_message(chat_id, "Ошибка скачивания файла.")
            return

        await bot.send_message(chat_id, "⏳ Обрабатываю файл...")

        transcript, structured_md, summary = await process_audio_or_video(file_path)

        # save outputs
        txt_path = "/tmp/transcript.txt"
        md_path = "/tmp/structured.md"
        sum_path = "/tmp/summary.txt"

        with open(txt_path, "w", encoding="utf-8") as f: f.write(transcript)
        with open(md_path, "w", encoding="utf-8") as f: f.write(structured_md)
        with open(sum_path, "w", encoding="utf-8") as f: f.write(summary)

        await bot.send_message(chat_id, "Готово! Отправляю файлы…")

        await bot.send_document(chat_id, FSInputFile(txt_path))
        await bot.send_document(chat_id, FSInputFile(md_path))
        await bot.send_document(chat_id, FSInputFile(sum_path))

    except Exception as e:
        logging.error(f"Worker error: {e}")
        logging.error(traceback.format_exc())

async def worker_loop():
    redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
    logging.info("Worker started.")

    while True:
        task = await redis_client.lpop("task_queue")
        if task:
            await process_task(task)
        else:
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(worker_loop())
