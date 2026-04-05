FROM python:3.11-slim

WORKDIR /app

# Cai cac thu vien he thong can thiet
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Cai Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Port 8000
EXPOSE 8000

# Chay FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
