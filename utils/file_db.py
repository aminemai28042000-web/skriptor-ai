import json
import os

DB_PATH = "database.json"

# Если база пустая — создадим
if not os.path.exists(DB_PATH):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump({}, f)


def load_db():
    """Загружает базу"""
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(data):
    """Сохраняет базу"""
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def increase_usage(user_id: int):
    """
    Увеличивает счётчик использования бота этим пользователем.
    Для будущих тарифов/лимитов.
    """

    user_id = str(user_id)
    db = load_db()

    if user_id not in db:
        db[user_id] = {"usage": 0}

    db[user_id]["usage"] += 1
    save_db(db)


def get_usage(user_id: int) -> int:
    """Возвращает количество использований пользователем."""

    db = load_db()
    user_id = str(user_id)

    if user_id not in db:
        return 0

    return db[user_id].get("usage", 0)
