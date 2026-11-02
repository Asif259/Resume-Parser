#!/usr/bin/env bash
# ==============================================================================
# Production SQLite Online Backup Script
# Performs non-blocking, safe online backups of resumes.db using SQLite backup API.
# ==============================================================================

set -euo pipefail

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATA_DIR="/opt/resume-parser/data"
DB_FILE="${DATA_DIR}/resumes.db"
BACKUP_DIR="/opt/resume-parser/backups"
LOG_FILE="/opt/resume-parser/logs/backup.log"

mkdir -p "$BACKUP_DIR" "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] $1" | tee -a "$LOG_FILE"
}

log "Starting database backup..."

if [[ ! -f "$DB_FILE" ]]; then
    log "Notice: Database file ${DB_FILE} does not exist yet. Skipping backup."
    exit 0
fi

TEMP_BACKUP="${BACKUP_DIR}/resumes_${TIMESTAMP}.tmp"
FINAL_BACKUP="${BACKUP_DIR}/resumes_${TIMESTAMP}.db.gz"

# 1. Execute online backup using SQLite's safe backup command
log "Creating online SQLite backup snapshot..."
if command -v sqlite3 &> /dev/null; then
    sqlite3 "$DB_FILE" ".backup '$TEMP_BACKUP'"
else
    # Fallback if sqlite3 CLI is inside the Docker container
    docker exec resume-parser-backend python3 -c "
import sqlite3, sys
src = sqlite3.connect('/app/data/resumes.db')
dst = sqlite3.connect('/app/data/backup_temp.db')
src.backup(dst)
dst.close()
src.close()
"
    mv "${DATA_DIR}/backup_temp.db" "$TEMP_BACKUP"
fi

# 2. Compress the snapshot with gzip
log "Compressing backup snapshot..."
gzip -9 -c "$TEMP_BACKUP" > "$FINAL_BACKUP"
rm -f "$TEMP_BACKUP"

# 3. Verify backup file integrity
log "Verifying compressed archive integrity..."
if gzip -t "$FINAL_BACKUP"; then
    BACKUP_SIZE=$(du -h "$FINAL_BACKUP" | cut -f1)
    log "Backup successfully created: ${FINAL_BACKUP} (Size: ${BACKUP_SIZE})"
    chmod 600 "$FINAL_BACKUP"
else
    log "ERROR: Backup integrity verification failed for ${FINAL_BACKUP}"
    rm -f "$FINAL_BACKUP"
    exit 1
fi

# 4. Prune backups older than 30 days
log "Pruning backups older than 30 days..."
DELETED_COUNT=$(find "$BACKUP_DIR" -name "resumes_*.db.gz" -type f -mtime +30 -print -delete | wc -l)
log "Pruned ${DELETED_COUNT} old backup archives."

log "Backup completed successfully."
