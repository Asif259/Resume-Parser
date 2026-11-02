#!/usr/bin/env bash
# ==============================================================================
# Model Artifact Transfer Script
# Syncs local DistilBERT NER model weights and configs to the Hostinger VPS.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOCAL_MODEL_DIR="${ROOT_DIR}/models/ner"

TARGET_HOST="${1:-}"

if [[ -z "$TARGET_HOST" ]]; then
    echo "Usage: $0 <user@vps-ip> [ssh-port]"
    echo "Example: $0 root@195.35.12.34 22"
    exit 1
fi

SSH_PORT="${2:-22}"
REMOTE_MODEL_DIR="/opt/resume-parser/models/ner"

echo "=== Verifying Local Model Files ==="
if [[ ! -d "$LOCAL_MODEL_DIR" ]]; then
    echo "Error: Local model directory $LOCAL_MODEL_DIR not found!"
    exit 1
fi

REQUIRED_FILES=("config.json" "tokenizer.json" "model.safetensors")
for file in "${REQUIRED_FILES[@]}"; do
    if [[ ! -f "${LOCAL_MODEL_DIR}/${file}" ]]; then
        echo "Error: Required model artifact ${file} missing from ${LOCAL_MODEL_DIR}!"
        exit 1
    fi
    echo "[✓] Verified ${file} ($(du -h "${LOCAL_MODEL_DIR}/${file}" | cut -f1))"
done

echo ""
echo "=== Transferring Model Weights to ${TARGET_HOST}:${REMOTE_MODEL_DIR} ==="
# Ensure remote directory exists
ssh -p "$SSH_PORT" "$TARGET_HOST" "mkdir -p ${REMOTE_MODEL_DIR}"

# Use rsync if available for progress and resume support, otherwise fall back to scp
if command -v rsync &> /dev/null; then
    rsync -avz --progress -e "ssh -p ${SSH_PORT}" \
        --include="model.safetensors" \
        --include="config.json" \
        --include="tokenizer.json" \
        --include="tokenizer_config.json" \
        --include="calibration.json" \
        --include="training_metrics.json" \
        --exclude="*" \
        "${LOCAL_MODEL_DIR}/" \
        "${TARGET_HOST}:${REMOTE_MODEL_DIR}/"
else
    echo "rsync not found locally, using scp..."
    scp -P "$SSH_PORT" "${LOCAL_MODEL_DIR}"/* "${TARGET_HOST}:${REMOTE_MODEL_DIR}/"
fi

# Set proper ownership on VPS
ssh -p "$SSH_PORT" "$TARGET_HOST" "chown -R 1000:1000 ${REMOTE_MODEL_DIR} && chmod 750 ${REMOTE_MODEL_DIR} && chmod 640 ${REMOTE_MODEL_DIR}/*"

echo ""
echo "=== Model Deployment Successful! ==="
echo "Files deployed to ${TARGET_HOST}:${REMOTE_MODEL_DIR}"
ssh -p "$SSH_PORT" "$TARGET_HOST" "ls -lh ${REMOTE_MODEL_DIR}"
