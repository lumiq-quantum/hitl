FROM python:3.12-slim

WORKDIR /app

COPY ./app ./app
COPY ./alembic ./alembic
COPY alembic.ini .
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
