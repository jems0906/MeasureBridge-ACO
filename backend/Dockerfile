FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app/backend

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app/ ./app/
COPY backend/alembic/ ./alembic/
COPY backend/scripts/ ./scripts/
COPY backend/alembic.ini ./alembic.ini
COPY fixtures/ /app/fixtures/

EXPOSE 8000
CMD ["sh", "-c", "python -m alembic upgrade head && python scripts/seed_demo.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]