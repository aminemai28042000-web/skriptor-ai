import re


def clean_raw_text(text: str) -> str:
    """Убираем мусор, системные символы и приводим к нормальному виду"""

    # удаляем двойные пробелы
    text = re.sub(r"\s+", " ", text)

    # убираем мусор в виде повторяющихся знаков
    text = re.sub(r"[—–-]{2,}", "-", text)

    # удаляем случайные спецсимволы
    text = re.sub(r"[^\S\r\n]+", " ", text)

    # отрезаем пустые строки
    text = text.strip()

    return text


def split_into_paragraphs(text: str) -> str:
    """Разбивает на абзацы — каждый абзац примерно по 3–4 предложения"""

    sentences = re.split(r"(?<=[.!?])\s+", text)
    paragraphs = []
    temp = []

    for sentence in sentences:
        temp.append(sentence)
        if len(temp) >= 3:
            paragraphs.append(" ".join(temp))
            temp = []

    if temp:
        paragraphs.append(" ".join(temp))

    return "\n\n".join(paragraphs)


def make_headers(text: str) -> str:
    """Добавляет визуальные 'блоки', чтобы текст выглядел структурно"""

    formatted = (
        "🟣 *Транскрипт*\n\n"
        + text
    )

    return formatted


def format_transcript(raw_text: str) -> str:
    """Главная функция форматирования"""

    cleaned = clean_raw_text(raw_text)
    paragraphs = split_into_paragraphs(cleaned)
    structured = make_headers(paragraphs)

    return structured
