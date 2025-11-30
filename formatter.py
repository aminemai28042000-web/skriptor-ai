import re
from openai import OpenAI

client = OpenAI()

# -------------------------------
#   Настройки
# -------------------------------

FILLERS = [
    "эээ", "э", "ну", "как бы", "типа", "в общем", "короче",
    "получается", "скажем так", "так сказать", "значит",
    "это самое", "например", "вот", "понимаешь", "как сказать"
]


# -------------------------------
#   Функции очистки текста
# -------------------------------

def remove_fillers(text: str) -> str:
    """Удаляет слова-паразиты."""
    for filler in FILLERS:
        text = re.sub(rf"\b{filler}\b", "", text, flags=re.IGNORECASE)
    return text


def normalize_spaces(text: str) -> str:
    """Удаляет лишние пробелы и нормализует текст."""
    text = re.sub(r"\s+", " ", text)
    text = text.replace(" .", ".")
    text = text.replace(" ,", ",")
    return text.strip()


def split_into_chunks(text: str, max_chars=4000):
    """Разделяет текст на части для отправки в GPT."""
    words = text.split()
    chunks = []
    current = []

    for w in words:
        current.append(w)
        if len(" ".join(current)) > max_chars:
            chunks.append(" ".join(current))
            current = []

    if current:
        chunks.append(" ".join(current))

    return chunks


# -------------------------------
#   GPT обработка текста
# -------------------------------

def gpt_process(chunk: str) -> dict:
    """
    Вызов GPT → возвращает структурированные данные:
    - formatted_text
    - key_ideas
    - terms
    - summary
    - lesson_plan
    """

    prompt = f"""
Обработай текст профессионально и структурированно.

Сделай ПЯТЬ блоков:

1) SUMMARY — краткое содержание в 5–10 предложениях
2) LESSON_PLAN — учебный план из 6–12 пунктов
3) KEY_IDEAS — список ключевых идей (минимум 10)
4) TERMS — список важных терминов и понятий
5) FORMATTED_TEXT — улучшенный структурированный текст:
   - абзацы
   - подзаголовки
   - логические блоки
   - литературная подача без паразитов

Используй следующий текст:

{chunk}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.choices[0].message.content

    # Парсим 5 секций
    result = {
        "summary": extract_section(raw, "SUMMARY"),
        "lesson_plan": extract_section(raw, "LESSON_PLAN"),
        "key_ideas": extract_section(raw, "KEY_IDEAS"),
        "terms": extract_section(raw, "TERMS"),
        "formatted_text": extract_section(raw, "FORMATTED_TEXT"),
    }

    return result


def extract_section(text: str, section: str) -> str:
    """Вынимает отдельные секции из GPT-ответа."""
    pattern = rf"{section}:(.*?)(?=\n[A-Z_]+:|$)"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""


# -------------------------------
#   Главная функция
# -------------------------------

def format_transcript(text: str) -> str:
    """
    Полная обработка транскрипта:
    - очистка
    - нормализация
    - GPT-структурирование
    - объединение всех секций
    """

    # 1. Очистка текста от мусора
    cleaned = remove_fillers(text)
    cleaned = normalize_spaces(cleaned)

    # 2. Деление на куски
    chunks = split_into_chunks(cleaned)

    summaries = []
    plans = []
    ideas = []
    terms = []
    formatted_parts = []

    # 3. Обработка каждого куска
    for chunk in chunks:
        result = gpt_process(chunk)

        summaries.append(result["summary"])
        plans.append(result["lesson_plan"])
        ideas.append(result["key_ideas"])
        terms.append(result["terms"])
        formatted_parts.append(result["formatted_text"])

    # 4. Объединение результатов
    final_text = [
        "# 📝 Краткое содержание",
        "\n".join(summaries),

        "\n\n# 📚 План урока",
        "\n".join(plans),

        "\n\n# 💡 Ключевые идеи",
        "\n".join(ideas),

        "\n\n# 🔤 Термины и понятия",
        "\n".join(terms),

        "\n\n# 📄 Структурированный текст",
        "\n\n".join(formatted_parts)
    ]

    return "\n".join(final_text)
