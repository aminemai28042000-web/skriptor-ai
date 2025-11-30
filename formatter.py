import re


# ---------------------------------------------------------
# Основной форматтер текста
# ---------------------------------------------------------
def format_transcript(text: str) -> str:
    text = _cleanup(text)
    paragraphs = _split_paragraphs(text)
    paragraphs = _add_auto_headings(paragraphs)

    return "\n\n".join(paragraphs).strip()


# ---------------------------------------------------------
# Чистим текст от мусора
# ---------------------------------------------------------
def _cleanup(text: str) -> str:
    # Убираем служебные символы
    text = text.replace("\r", "").strip()

    # Убираем повторяющиеся переносы
    text = re.sub(r"\n{2,}", "\n", text)

    # Паразитные слова / междометия
    filler_words = [
        r"\bэ+?м*\b", r"\bэээ+?\b", r"\bну\b", r"\bкак бы\b",
        r"\bтипа\b", r"\bполучается\b", r"\bзначит\b", r"\bв общем\b"
    ]
    for w in filler_words:
        text = re.sub(w, "", text, flags=re.IGNORECASE)

    # Удаляем двойные пробелы
    text = re.sub(r" {2,}", " ", text)

    return text.strip()


# ---------------------------------------------------------
# Разбиваём на абзацы по смыслу
# ---------------------------------------------------------
def _split_paragraphs(text: str) -> list:
    sentences = re.split(r"(?<=[.!?])\s+", text)

    paragraphs = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) < 300:  # удобная длина абзаца
            current += sentence + " "
        else:
            paragraphs.append(current.strip())
            current = sentence + " "

    if current.strip():
        paragraphs.append(current.strip())

    return paragraphs


# ---------------------------------------------------------
# Автоматические подзаголовки
# ---------------------------------------------------------
def _add_auto_headings(paragraphs: list) -> list:
    final = []

    for p in paragraphs:

        # если абзац длинный — делаем его отдельным смысловым блоком
        if len(p) > 350:
            final.append("## 📌 Новый смысловой блок")
            final.append(p)
            continue

        # ключевые фразы → заголовки
        triggers = ["итог", "вывод", "главное", "важно", "первое", "второе"]
        if any(p.lower().startswith(t) for t in triggers):
            p = "### " + p.capitalize()
            final.append(p)
            continue

        final.append(p)

    return final
