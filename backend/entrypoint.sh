#!/bin/bash
set -e

echo "=== Starting NLP Resume Parser Backend ==="
echo "Environment: ${APP_ENV:-production}"
echo "Model Directory: ${MODEL_DIR:-/app/models/ner}"
echo "Database URL: ${DATABASE_URL:-sqlite:////app/data/resumes.db}"
echo "Upload Directory: ${UPLOAD_DIR:-/app/uploads}"

# Verify persistent directories exist
mkdir -p "${UPLOAD_DIR:-/app/uploads}"
mkdir -p "${MODEL_DIR:-/app/models/ner}"
mkdir -p "/app/data"
mkdir -p "${HF_HOME:-/app/cache/huggingface}"

# Check for custom DistilBERT NER model
if [ -f "${MODEL_DIR}/model.safetensors" ] && [ -f "${MODEL_DIR}/config.json" ]; then
    echo "[✓] Custom DistilBERT NER model detected at ${MODEL_DIR}"
else
    echo "[!] Notice: Custom DistilBERT model weights (model.safetensors) not found at ${MODEL_DIR}."
    echo "    Backend will operate with spaCy & regex rules until weights are mounted."
fi

# Execute main process
exec "$@"
