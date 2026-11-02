#!/usr/bin/env bash
# ==============================================================================
# Production Emergency Rollback Script
# Rolls back backend Docker container to previous image and optionally restores database.
# ==============================================================================

set -euo pipefail

APP_DIR="/opt/resume-parser/app"
DATA_DIR="/opt/resume-parser/data"
BACKUP_DIR="/opt/resume-parser/backups"

echo "=== NLP Resume Parser Rollback Utility ==="

echo "Choose action:"
echo "1) Rollback Docker container to previous image tag"
echo "2) Restore SQLite database from backup archive"
echo "3) Perform full service restart and health check"
read -rp "Enter choice [1-3]: " CHOICE

case "$CHOICE" in
    1)
        echo "Rolling back Docker image..."
        cd "$APP_DIR"
        if docker images | grep -q "resume-parser-backend.*previous"; then
            docker tag resume-parser-backend:previous resume-parser-backend:latest
            docker compose up -d --no-build
            echo "[✓] Container restarted with previous image."
        else
            echo "Error: No 'resume-parser-backend:previous' tag found."
            echo "Available images:"
            docker images resume-parser-backend
            exit 1
        fi
        ;;
    2)
        echo "Available database backups in ${BACKUP_DIR}:"
        ls -lh "${BACKUP_DIR}"/resumes_*.db.gz 2>/dev/null || { echo "No backups found!"; exit 1; }
        read -rp "Enter the full path of the backup file to restore: " RESTORE_FILE
        if [[ ! -f "$RESTORE_FILE" ]]; then
            echo "Error: File $RESTORE_FILE does not exist."
            exit 1
        fi

        echo "Stopping backend container before restoring database..."
        cd "$APP_DIR" && docker compose stop backend

        # Archive current state first
        CURRENT_BACKUP="${DATA_DIR}/resumes_pre_restore_$(date +%Y%m%d_%H%M%S).db"
        if [[ -f "${DATA_DIR}/resumes.db" ]]; then
            cp "${DATA_DIR}/resumes.db" "$CURRENT_BACKUP"
            echo "Preserved current DB to $CURRENT_BACKUP"
        fi

        echo "Decompressing and restoring to ${DATA_DIR}/resumes.db..."
        gzip -dc "$RESTORE_FILE" > "${DATA_DIR}/resumes.db"
        chown 1000:1000 "${DATA_DIR}/resumes.db"
        chmod 600 "${DATA_DIR}/resumes.db"

        echo "Restarting backend container..."
        docker compose start backend
        echo "[✓] Database restored and container started."
        ;;
    3)
        echo "Restarting backend service..."
        cd "$APP_DIR" && docker compose restart backend
        ;;
    *)
        echo "Invalid option."
        exit 1
        ;;
esac

echo ""
echo "=== Running Health Check ==="
sleep 5
if curl -sf http://127.0.0.1:8000/health; then
    echo ""
    echo "[✓] Service is healthy!"
else
    echo ""
    echo "[!] Health check failed. Check logs: docker compose logs backend"
fi

