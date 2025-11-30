FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg wget curl && \
    pip install yt-dlp && \
    apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "bot.py"]
