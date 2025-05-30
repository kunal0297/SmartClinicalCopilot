FROM python:3.9-slim-bullseye as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3.9-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY backend/requirements.txt .

# Install Python packages in stages to handle timeouts
RUN pip install --no-cache-dir --timeout 1000 --upgrade pip && \
    pip install --no-cache-dir --timeout 1000 fastapi uvicorn pydantic pydantic-settings python-dotenv python-multipart httpx pyyaml aiohttp requests && \
    pip install --no-cache-dir --timeout 1000 sqlalchemy psycopg2-binary alembic && \
    pip install --no-cache-dir --timeout 1000 openai tenacity scikit-learn numpy shap && \
    pip install --no-cache-dir --timeout 1000 fhirclient prometheus-client prometheus-fastapi-instrumentator python-json-logger && \
    pip install --no-cache-dir --timeout 1000 cryptography redis[hiredis] aiofiles click rich tabulate cachetools && \
    pip install --no-cache-dir --timeout 1000 transformers ollama python-jose passlib bcrypt && \
    pip install --no-cache-dir --timeout 1000 pytest pytest-asyncio pytest-cov black isort flake8 mypy PyJWT && \
    pip install --no-cache-dir --timeout 1000 experta

# Install PyTorch separately with CPU-only version
RUN pip install --no-cache-dir --timeout 1000 torch==2.0.1 --index-url https://download.pytorch.org/whl/cpu

# Final stage
FROM python:3.9-slim-bullseye

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Copy the rest of the application
COPY backend/ .
COPY static/ /app/static/

# Debug: List files to verify demo_patients.json is present
RUN ls -la /app

# Debug: List backend directory contents
RUN ls -la /app/backend

# Create necessary directories
RUN mkdir -p rules logs data cache static

# Build C extensions
RUN python setup.py build_ext --inplace

# Expose the port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DATABASE_URL=postgresql://postgres:postgres@db:5432/clinical_copilot
ENV IRIS_HOST=iris
ENV IRIS_PORT=52773
ENV IRIS_NAMESPACE=USER

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 