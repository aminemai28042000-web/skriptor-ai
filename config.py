import os
from dotenv import load_dotenv

load_dotenv()

# -----------------------------------------
# Telegram
# -----------------------------------------
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")   # Главное имя
if not BOT_TOKEN:
    raise ValueError("ERROR: TELEGRAM_BOT_TOKEN not set in environment")

# -----------------------------------------
# OpenAI
# -----------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("ERROR: OPENAI_API_KEY not set in environment")

# -----------------------------------------
# Allowed file size
# -----------------------------------------
MAX_FILE_SIZE_MB = 2000   # 2 GB
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# -----------------------------------------
# Webhook configuration
# -----------------------------------------
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")   # например: https://skriptor-ai-z1s7.onrender.com
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH")   #например /webhook/<token>

if not WEBHOOK_HOST:
    raise ValueError("ERROR: WEBHOOK_HOST not set")

if not WEBHOOK_PATH:
    raise ValueError("ERROR: WEBHOOK_PATH not set")

WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "skriptor_secret")

# -----------------------------------------
# Redis
# -----------------------------------------
REDIS_URL = os.getenv("REDIS_URL")  # например upstash URL
if not REDIS_URL:
    raise ValueError("ERROR: REDIS_URL not set")

# -----------------------------------------
# Temp folder
# -----------------------------------------
TEMP_DIR = "/app/temp"
os.makedirs(TEMP_DIR, exist_ok=True)
