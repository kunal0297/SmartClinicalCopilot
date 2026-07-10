FROM python:3.11-slim-bookworm

WORKDIR /app

# System dependencies:
#  - build-essential/gcc: build the optional C trie extension & any wheels
#  - curl: used by the Docker Compose healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better layer caching.
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code as a package
COPY backend /app/backend

# Copy the runtime data the app reads from the working directory
COPY rules /app/rules
COPY demo_patients.json /app/demo_patients.json

# Create runtime directories
RUN mkdir -p /app/backend/rules /app/backend/logs /app/backend/data /app/backend/cache

# Build the optional C trie extension. The app falls back to a pure-Python
# implementation, so a build failure here must not break the image.
RUN cd /app/backend && (python setup.py build_ext --inplace || \
    echo "C extension build skipped; using pure-Python trie engine.")

EXPOSE 8000

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000

# Start the application
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
