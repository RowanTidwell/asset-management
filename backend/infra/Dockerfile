FROM python:3.14-slim

WORKDIR /app

# system deps for psycopg2
RUN apt-get update && apt-get install -y build-essential libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "asset_management_server.main:app", "--host", "0.0.0.0", "--port", "8000"]
