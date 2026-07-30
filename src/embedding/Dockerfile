FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY app.py .

HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:5100/health || exit 1

EXPOSE 5100

CMD ["python", "app.py"]
