
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


COPY backend ./backend
COPY frontend ./frontend

# Expose app port
EXPOSE 8000

# Run app with uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
