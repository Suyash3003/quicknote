FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DB_PATH=/data/notes.db

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN useradd --uid 10001 --create-home quicknote \
    && mkdir -p /data \
    && chown quicknote:quicknote /data

COPY app.py .
COPY templates/ templates/
COPY static/ static/

USER quicknote

VOLUME ["/data"]

EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=3)"

CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:8080", "app:app"]
