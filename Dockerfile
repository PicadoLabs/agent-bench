# Multi-stage Dockerfile: Build Frontend + Python Backend
FROM node:20-slim AS frontend-builder
WORKDIR /build
COPY frontend/package.json frontend/
RUN cd frontend && npm install
COPY frontend/ frontend/
RUN cd frontend && npm run build

FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ backend/
COPY benchmarks/ benchmarks/
COPY agentbench.py .
COPY .env.example .env

COPY --from=frontend-builder /build/frontend/dist frontend/dist

EXPOSE 8000
CMD ["python", "backend/main.py"]

