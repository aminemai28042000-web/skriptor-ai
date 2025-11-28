import os
import csv
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "logs.csv")

os.makedirs(LOG_DIR, exist_ok=True)


def log_event(user_id, event_type, data):
    """
    Логирует любое событие в CSV:

    user_id — айди пользователя
    event_type — тип события: text_input, file_input, complete, error
    data — описание события
    """

    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        user_id,
        event_type,
        data
    ]

    new_file = not os.path.exists(LOG_FILE)

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["timestamp", "user_id", "event", "data"])
        writer.writerow(row)
