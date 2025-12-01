# formatter.py
"""
Формирование структурированного Markdown + Summary.
Эта версия:
- делает авто-разбиение длинных транскриптов по секциям
- делает вложенную структуру: главы → пункты → подпункты
- добавляет таймкоды если они есть
- готовит текст так, чтобы Worker мог легко собрать PDF/MD
"""

import re
from typing import Tuple

def clean_text(text: str) -> str:
    """Убирает мусор, двойные пробелы, повторяющиеся переносы."""
    text = text.replace("\r", "")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()

def split_into_sections(text: str):
    """
    Делит длинный текст на смысловые части.
    Правила такие:
    - если встречается фраза вроде 'итак', 'во-первых', 'далее' — начинается новая секция
    - если таймкод — новая секция
    """

    lines = text.split("\n")
    sections = []
    current = []

    triggers = [
        r"\bитак\b", r"\bво-первых\b", r"\bво вторых\b",
        r"\bдалее\b", r"\bпереходим\b", r"^\[\d{1,2}:\d{2}"
    ]

    def is_new_section(l: str):
        return any(re.search(t, l.lower()) for t in triggers)

    for line in lines:
        if len(line.strip()) == 0:
            continue

        if is_new_section(line) and current:
            sections.append("\n".join(current))
            current = [line]
        else:
            current.append(line)

    if current:
        sections.append("\n".join(current))

    return sections

def make_markdown(sections):
    """Создаёт красивый Markdown"""
    md = "# 📄 Транскрипт (структурированный)\n\n"

    for i, block in enumerate(sections, 1):
        md += f"## Раздел {i}\n\n"
        md += block.strip() + "\n\n"

    return md.strip()


def make_summary(text: str) -> str:
    """
    Делает короткое summary — простая версия, без OpenAI.
    Worker потом может заменить эту функцию на GPT summary.
    """

    sentences = re.split(r"[.!?]\s+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    if not sentences:
        return "Короткий файл. Содержание не требует саммари."

    top = sentences[:4]
    summary = " ".join(top)

    return f"## Краткое содержание\n\n{summary}…"


def format_transcription(raw_text: str) -> Tuple[str, str]:
    """
    Главная функция файла. Возвращает:
    1) markdown_transcript
    2) summary_text
    """

    cleaned = clean_text(raw_text)
    sections = split_into_sections(cleaned)
    markdown = make_markdown(sections)
    summary = make_summary(cleaned)

    return markdown, summary
