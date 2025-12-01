# ------------------------------------------------------
# BASE IMAGE
# ------------------------------------------------------
FROM python:3.10-slim

WORKDIR /app

# ------------------------------------------------------
# SYSTEM DEPENDENCIES
# ------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc ffmpeg supervisor \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------
# COPY PROJECT FILES
# ------------------------------------------------------
COPY . .

# ------------------------------------------------------
# PYTHON DEPENDENCIES (С НУЛЯ, БЕЗ КЭША)
# ------------------------------------------------------
# !!! Самое важное — уничтожаем устаревший openai, который вызывает ошибку
RUN pip uninstall -y openai || true

# Полное удаление PIP-кэша
RUN pip cache purge || true

# Устанавливаем требования принудительно, без кэша
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --force-reinstall -r requirements.txt

# ------------------------------------------------------
# SUPERVISOR CONFIG
# ------------------------------------------------------
RUN mkdir -p /var/log/supervisor

# Supervisord: API + Worker + встроенный Redis
RUN printf "[supervisord]\nnodaemon=true\n\n\
[program:api]\ncommand=uvicorn server:app --host 0.0.0.0 --port 8000\nautostart=true\nautorestart=true\nstdout_logfile=/dev/stdout\nstderr_logfile=/dev/stderr\n\n\
[program:worker]\ncommand=python worker.py\nautostart=true\nautorestart=true\nstdout_logfile=/dev/stdout\nstderr_logfile=/dev/stderr\n\n\
[program:redis]\ncommand=redis-server --save \"900 1\" --save \"300 10\" --save \"60 10000\"\nautostart=true\nautorestart=true\nstdout_logfile=/dev/stdout\nstderr_logfile=/dev/stderr\n" \
> /etc/supervisor/conf.d/supervisord.conf

# ------------------------------------------------------
# APP PORT
# ------------------------------------------------------
EXPOSE 8000

# ------------------------------------------------------
# ENTRYPOINT
# ------------------------------------------------------
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
