#!/usr/bin/env bash
# ==============================================================================
# Hostinger VPS Provisioning and Production Setup Script
# Target OS: Ubuntu 24.04 LTS (x86_64)
# ==============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 1. Root Check
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root or with sudo."
    exit 1
fi

log_info "Starting Hostinger VPS production preparation..."

# 2. Update and upgrade system packages
log_info "Updating system packages..."
apt-get update -y
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

# 3. Install core dependencies
log_info "Installing core system tools, Nginx, Certbot, and SQLite3..."
apt-get install -y --no-install-recommends \
    curl \
    wget \
    git \
    ufw \
    ca-certificates \
    gnupg \
    lsb-release \
    nginx \
    certbot \
    python3-certbot-nginx \
    sqlite3 \
    logrotate

# 4. Install Docker Engine and Docker Compose Plugin if not installed
if ! command -v docker &> /dev/null; then
    log_info "Installing Docker Engine..."
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    systemctl enable docker
    systemctl start docker
    log_success "Docker Engine installed successfully."
else
    log_info "Docker is already installed."
fi

# 5. Configure UFW Firewall
log_info "Configuring UFW firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw --force enable
log_success "UFW configured (Ports 22, 80, 443 allowed)."

# 6. Setup Production Directory Structure at /opt/resume-parser
log_info "Setting up production persistent storage at /opt/resume-parser..."
APP_DIR="/opt/resume-parser"
mkdir -p \
    "${APP_DIR}/data" \
    "${APP_DIR}/uploads" \
    "${APP_DIR}/models/ner" \
    "${APP_DIR}/cache/huggingface" \
    "${APP_DIR}/backups" \
    "${APP_DIR}/logs" \
    "${APP_DIR}/scripts"

# Set ownership to UID 1000 (appuser in container)
chown -R 1000:1000 \
    "${APP_DIR}/data" \
    "${APP_DIR}/uploads" \
    "${APP_DIR}/models" \
    "${APP_DIR}/cache"

chmod -R 750 "${APP_DIR}"
chmod 700 "${APP_DIR}/data" "${APP_DIR}/backups"
log_success "Persistent directories initialized with restricted permissions."

# 7. Configure Nginx Security Snippets and ACME webroot
mkdir -p /var/www/certbot /etc/nginx/snippets
cat <<'EOF' > /etc/nginx/snippets/security-headers.conf
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
EOF

# 8. Configure Log Rotation
cat <<EOF > /etc/logrotate.d/resume-parser
/opt/resume-parser/logs/*.log /var/log/nginx/resume_api_*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 \$(cat /var/run/nginx.pid)
    endscript
}
EOF

# 9. Install automated daily database backup cron job
log_info "Configuring daily SQLite backup cron job..."
if [ -f "${APP_DIR}/scripts/backup-db.sh" ]; then
    chmod +x "${APP_DIR}/scripts/backup-db.sh"
    # Run daily at 03:00 UTC
    CRON_LINE="0 3 * * * ${APP_DIR}/scripts/backup-db.sh >> /opt/resume-parser/logs/backup.log 2>&1"
    (crontab -l 2>/dev/null | grep -F -v "backup-db.sh" || true; echo "$CRON_LINE") | crontab -
    log_success "Daily backup cron registered."
fi

log_success "=========================================================="
log_success "VPS Provisioning Complete!"
log_success "Next steps:"
log_success "1. Clone repo to /opt/resume-parser/app"
log_success "2. Copy .env to /opt/resume-parser/app/.env"
log_success "3. Transfer models using scripts/deploy-model.sh"
log_success "4. Configure Nginx site: /etc/nginx/sites-available/resume-parser-api.conf"
log_success "5. Run: certbot --nginx -d api.YOUR_DOMAIN.com"
log_success "6. Run: docker compose up -d --build"
log_success "=========================================================="

