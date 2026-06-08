FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m -u 1000 appuser

COPY --chown=appuser:appuser __init__.py .
COPY --chown=appuser:appuser templates ./templates

EXPOSE 5000

USER appuser

CMD ["python", "__init__.py"]
