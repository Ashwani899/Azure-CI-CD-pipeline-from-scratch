# --- Build stage ---
FROM python:3.11-slim AS base

WORKDIR /app

# Install dependencies first so Docker can cache this layer between builds
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ .

# These get overridden at build time by the pipeline (see azure-pipelines.yml)
ARG BUILD_ID=local-dev
ARG BUILD_TIME=not-set
ENV BUILD_ID=$BUILD_ID
ENV BUILD_TIME=$BUILD_TIME
ENV PORT=8000

EXPOSE 8000

# gunicorn instead of the Flask dev server — this is what Azure App Service
# actually expects to talk to in production
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main:app"]
