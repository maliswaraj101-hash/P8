FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 4000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "4000"]

# server.py contains our server and app if for app = Fastapi()