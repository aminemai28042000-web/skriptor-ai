# ----------------------------
#  Base image
# ----------------------------
FROM python:3.10-slim

# ----------------------------
#  System dependencies
# ----------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ----------------------------
#  Workspace
# ----------------------------
WORKDIR /app

# ----------------------------
#  Copy requirements first (cache)
# ----------------------------
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------
#  Copy project
# ----------------------------
COPY . .

# ----------------------------
#  Environment
# ----------------------------
ENV PYTHONUNBUFFERED=1
ENV AIOHTTP_CLIENT_MAX_SIZE=2147483648   # 2 GB

# ----------------------------
#  Expose webhook port
# ----------------------------
EXPOSE 8000

# ----------------------------
#  Start command
# ----------------------------
CMD ["python", "server.py"]
