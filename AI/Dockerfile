# Dockerfile for TechStore AI Model Microservice
FROM python:3.11-slim

WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications
COPY requirements.txt ./

# Install python dependencies including fastapi and uvicorn
RUN pip install --no-cache-dir -r requirements.txt fastapi==0.143.2 uvicorn[standard]

# Copy AI code only (.dockerignore keeps out .env, models, data, runtime);
# docker-compose.yml mounts data/ and runtime/ and passes configuration as env.
COPY . .

# Expose internal microservice port
EXPOSE 8000

ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Start FastAPI inference server
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
