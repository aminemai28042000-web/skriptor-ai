import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Allowed max size
MAX_FILE_SIZE_MB = 2000     # 2 GB
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Webhook configuration
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "skriptor_secret")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Render URL + /webhook

# Redis (Render/Upstash)
REDIS_URL = os.getenv("REDIS_URL")  # Example: redis://default:KEY@usw1-merry-lemur-12345.upstash.io:6379

# Temp folder
TEMP_DIR = "/app/temp"
os.makedirs(TEMP_DIR, exist_ok=True)
