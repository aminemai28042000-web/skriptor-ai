FROM python:3.10-slim

# обновление системы
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        redis-server \
        supervisor \
        ffmpeg \
        wget \
        curl \
        git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# копируем зависимости
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# копируем проект
COPY . .

# копируем конфиг supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Разрешить большие файлы
ENV AIOHTTP_CLIENT_MAX_SIZE=2147483648

EXPOSE 8000

CMD ["/usr/bin/supervisord"]
