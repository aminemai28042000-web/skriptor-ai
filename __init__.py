"""
Инициализация пакета skriptor-ai.

Этот файл:
- делает проект корректно импортируемым
- устраняет ошибки вида "Cannot import..."
- хранит общую информацию о пакете
- проверяет совместимость Python
"""

import sys
import logging

__package_name__ = "skriptor-ai"
__version__ = "1.0.0"
__description__ = "AI Telegram Bot with webhook, worker, downloader and transcription."

# Логирование загрузки модуля
logging.basicConfig(level=logging.INFO)
logging.info(f"📦 Загружен пакет {__package_name__} v{__version__}")

# Проверка Python версии
MIN_PYTHON = (3, 10)
if sys.version_info < MIN_PYTHON:
    raise RuntimeError(
        f"{__package_name__} требует Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+, "
        f"обнаружено: {sys.version_info.major}.{sys.version_info.minor}"
    )

# Ничего не импортируем, чтобы избежать циклических зависимостей.
