#!/bin/bash
echo "DEBUG: Entrypoint script started."
echo "DEBUG: Running uvicorn command..."
exec uvicorn backend.app:app --host 0.0.0.0 --port 8000 