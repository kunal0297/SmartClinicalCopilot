#!/bin/bash

echo "🚀 Starting FHIR resource upload..."

# Default values; can be overridden by environment variables or arguments
FHIR_URL="${FHIR_URL:-http://localhost:5001/fhir/r4}"
RESOURCE_DIR="${RESOURCE_DIR:-/usr/irissys/Startup/SamplePatients}"
LOG_FILE="${LOG_FILE:-/usr/irissys/Startup/fhir_upload.log}"
MAX_RETRIES=3
RETRY_DELAY=2

# Log all output
exec > >(tee -i "$LOG_FILE")
exec 2>&1

# Check if FHIR server is reachable
if ! curl --output /dev/null --silent --head --fail "$FHIR_URL"; then
  echo " FHIR server is not reachable at $FHIR_URL"
  exit 1
fi

echo " Uploading files from: $RESOURCE_DIR"
echo " FHIR server: $FHIR_URL"

upload_failed=0

for file in "$RESOURCE_DIR"/*.json; do
  if [[ -f "$file" ]]; then
    echo " Uploading $(basename "$file")..."

    # Validate JSON
    if ! jq empty "$file" 2>/dev/null; then
      echo " Invalid JSON in file: $(basename "$file")"
      upload_failed=1
      continue
    fi

    # Retry logic
    attempt=1
    while [[ $attempt -le $MAX_RETRIES ]]; do
      http_code=$(curl -s -w "%{http_code}" -o /dev/null -X POST "$FHIR_URL" \
        -H "Content-Type: application/fhir+json" \
        -d @"$file")

      if [[ "$http_code" -ge 200 && "$http_code" -lt 300 ]]; then
        echo " Uploaded successfully."
        break
      else
        echo "  Attempt $attempt failed. HTTP status: $http_code"
        if [[ $attempt -lt $MAX_RETRIES ]]; then
          echo " Retrying in $RETRY_DELAY seconds..."
          sleep $RETRY_DELAY
        fi
        ((attempt++))
      fi
    done

    # If max retries reached and upload failed
    if [[ $attempt -gt $MAX_RETRIES ]]; then
      echo " Failed to upload $(basename "$file") after $MAX_RETRIES attempts."
      upload_failed=1
    fi
  fi
done

if [[ $upload_failed -eq 1 ]]; then
  echo " Some FHIR resources failed to upload. Check the log at $LOG_FILE"
  exit 1
else
  echo " All sample FHIR resources uploaded successfully."
fi
