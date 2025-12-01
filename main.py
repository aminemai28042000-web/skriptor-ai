import sys
import asyncio
import logging
from typing import Optional

from server import start_webhook
from worker import start_worker


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


async def safe_run(coro, name: str):
    """
    Универсальный безопасный запуск server/worker
    с перехватом ошибок и автоматическим логированием.
    """
    try:
        logging.info(f"🚀 Запуск компонента: {name}...")
        await coro
    except asyncio.CancelledError:
        logging.warning(f"⛔ {name} остановлен (CancelledError).")
    except Exception as e:
        logging.error(f"❌ Ошибка в {name}: {e}", exc_info=True)


def parse_mode(arg: Optional[str]) -> str:
    """
    Возвращает режим работы:
        - server
        - worker
    """
    if arg is None:
        return "server"

    arg = arg.lower().strip()
    if arg in ("server", "worker"):
        return arg

    logging.warning(f"Неизвестный режим: {arg}. Используется server.")
    return "server"


async def main():
    """
    Главная точка входа для локального запуска.

    Примеры:
        python main.py server
        python main.py worker
    """
    mode = parse_mode(sys.argv[1] if len(sys.argv) > 1 else None)

    logging.info(f"🔧 Режим запуска: {mode}")

    if mode == "server":
        await safe_run(start_webhook(), "Webhook Server")

    elif mode == "worker":
        await safe_run(start_worker(), "Background Worker")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("🛑 Приложение остановлено пользователем (Ctrl+C).")
