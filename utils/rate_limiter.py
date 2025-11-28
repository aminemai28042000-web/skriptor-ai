import time

# user_id → timestamp последнего запроса
RATE_LIMIT = {}
LIMIT_SECONDS = 30   # 1 запрос в 30 сек


def is_rate_limited(user_id: int) -> bool:
    """
    Возвращает:
    True — если пользователю нужно подождать
    False — если можно выполнять следующий запрос
    """

    now = time.time()

    # Если пользователь впервые — нет лимита
    if user_id not in RATE_LIMIT:
        RATE_LIMIT[user_id] = now
        return False

    last_time = RATE_LIMIT[user_id]

    if now - last_time < LIMIT_SECONDS:
        # Превышен лимит
        return True

    # Обновляем timestamp
    RATE_LIMIT[user_id] = now
    return False
