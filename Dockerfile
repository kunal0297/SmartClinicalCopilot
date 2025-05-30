FROM python:3.9-slim-bullseye

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3.9-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install docker psutil

# Copy backend code as a package
COPY backend /app/backend

# Debug: List files to verify backend directory is present
RUN ls -la /app
RUN ls -la /app/backend

# Create necessary directories (adjust paths if needed based on your app structure)
RUN mkdir -p /app/backend/rules /app/backend/logs /app/backend/data /app/backend/cache

# Build C extensions (adjust path if setup.py is in a different location)
WORKDIR /app/backend
RUN python setup.py build_ext --inplace
WORKDIR /app

# Expose the port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DATABASE_URL=postgresql://postgres:postgres@db:5432/clinical_copilot
ENV IRIS_HOST=iris
ENV IRIS_PORT=52773
ENV IRIS_NAMESPACE=USER

# Start the application
RUN pip list
RUN python --version
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"] 