import re


# ---------------------------------------------------------
# Основная функция форматирования транскрипта
# ---------------------------------------------------------
def format_transcript(text: str) -> str:
    """
    Принимает сырой текст из транскрибера и превращает его в
    удобочитаемый структурированный конспект.
    """

    # Удаляем лишние пробелы и разрывы строк
    text = text.replace("\r", "")
    text = re.sub(r"\n{2,}", "\n", text).strip()

    # Удаляем паразитные слова
    filler_words = [
        r"\bээ+?\b", r"\bэээ+?\b", r"\bну\b", r"\bкак бы\b",
        r"\bполучается\b", r"\bтипа\b", r"\bзначит\b"
    ]
    for w in filler_words:
        text = re.sub(w, "", text, flags=re.IGNORECASE)

    # Превращаем длинные простыни текста в абзацы
    text = _split_into_paragraphs(text)

    # Добавляем заголовки (эвристики)
    text = _add_headings(text)

    return text.strip()


# ---------------------------------------------------------
# Разбиваем на абзацы
# ---------------------------------------------------------
def _split_into_paragraphs(text: str) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    paragraphs = []
    chunk = ""

    for s in sentences:
        chunk += s + " "
        if len(chunk) > 250:   # если абзац слишком длинный – переносим
            paragraphs.append(chunk.strip())
            chunk = ""

    if chunk:
        paragraphs.append(chunk.strip())

    return "\n\n".join(paragraphs)


# ---------------------------------------------------------
# "Автоматические" заголовки
# ---------------------------------------------------------
def _add_headings(text: str) -> str:
    paragraphs = text.split("\n\n")
    formatted = []

    for p in paragraphs:
        # Если абзац начинается со слов "тема", "итог", "важно"
        if re.match(r"^(итог|вывод|важно|ключевое|главное)\b", p, flags=re.IGNORECASE):
            p = "## " + p.capitalize()

        # Если абзац длиннее 350 символов – добавляем визуальный разделитель
        if len(p) > 350:
            formatted.append("## Новый блок\n" + p)
        else:
            formatted.append(p)

    return "\n\n".join(formatted)
