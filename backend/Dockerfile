FROM ollama/ollama:latest

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    OLLAMA_API_BASE=http://127.0.0.1:11434/api \
    OLLAMA_MODEL=llama3.2:1b

RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip curl ca-certificates && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/python3 /usr/local/bin/python

COPY requirements.txt ./
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY . /app
RUN chmod +x /app/start.sh

EXPOSE 8000

ENTRYPOINT ["/app/start.sh"]
