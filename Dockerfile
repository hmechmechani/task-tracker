FROM python:3.11-slim AS builder
WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim
WORKDIR /app

RUN useradd --no-create-home --shell /usr/sbin/nologin app

COPY --from=builder /install /usr/local
COPY app ./app
RUN chown -R app:app /app

EXPOSE 8000

USER app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
