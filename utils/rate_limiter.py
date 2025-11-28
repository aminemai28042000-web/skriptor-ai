import time

# минимальный интервал между запросами
RATE_LIMIT_SECONDS = 15

# храним время последнего запроса от каждого пользователя
last_request_time = {}


def is_allowed(user_id: int) -> bool:
    """
    Проверяет, можно ли пользователю выполнять новый запрос.
    """
    current_time = time.time()

    if user_id not in last_request_time:
        last_request_time[user_id] = current_time
        return True

    if current_time - last_request_time[user_id] >= RATE_LIMIT_SECONDS:
        last_request_time[user_id] = current_time
        return True

    return False


def get_wait_message(user_id: int) -> str:
    """
    Сообщение, которое бот отправляет пользователю,
    если нужно подождать.
    """
    last_time = last_request_time.get(user_id, 0)
    wait = RATE_LIMIT_SECONDS - (time.time() - last_time)

    if wait < 1:
        wait = 1

    return f"⏳ Пожалуйста, подождите {int(wait)} секунд перед следующим запросом."
