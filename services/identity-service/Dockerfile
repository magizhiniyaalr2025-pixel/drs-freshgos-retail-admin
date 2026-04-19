FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y gcc

# Copy ONLY identity-service contents into /app
COPY services/identity-service /app

# Copy shared lib
COPY common-lib /common-lib

# Install dependencies
RUN pip install --no-cache-dir /common-lib
RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
