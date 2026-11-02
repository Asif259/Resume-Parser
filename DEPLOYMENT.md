# Production Deployment Guide: NLP-Based Resume Parser

This guide provides the complete, step-by-step production deployment procedures for the **NLP-Based Resume Parser**.

---

## 1. Architecture Overview

```text
                           INTERNET
                              │
                              ▼
                         USER BROWSER
                              │
                     HTTPS REQUESTS (TLS)
                              │
             ┌────────────────┴────────────────┐
             ▼                                 ▼
      VERCEL HOSTING                     HOSTINGER VPS
  (app.YOUR_DOMAIN.com)               (api.YOUR_DOMAIN.com)
             │                                 │
     Next.js 16 (React 19)              Nginx (Reverse Proxy)
     Tailwind CSS 4 UI                 Rate Limiting & SSL
             │                                 │
             │                             HTTP :8000
             │                                 ▼
             │                        Docker Container (Backend)
             │                           FastAPI + Uvicorn
             │                           PyTorch CPU Wheels
             │                           spaCy (en_core_web_sm)
             │                           SentenceTransformers (all-MiniLM-L6-v2)
             │                           DistilBERT NER Model
             │                           Tesseract OCR + PyMuPDF
             │                                 │
             │                       ┌─────────┴─────────┐
             │                       ▼                   ▼
             │                 Host Volumes         Host Volumes
             │                /opt/resume-parser/   /opt/resume-parser/
             │                   data/resumes.db       models/ner/
             │                   uploads/              cache/huggingface/
             │
             └────────────── REST API Calls ───────────────►
```

---

## 2. DNS Configuration

Configure the following records with your DNS registrar (e.g., Hostinger DNS, Cloudflare, Namecheap):

| Type | Host / Name | Target / Destination | Purpose |
|------|-------------|----------------------|---------|
| `A` | `api` | `<HOSTINGER_VPS_IPV4>` | Points backend subdomain to Hostinger VPS |
| `CNAME` or `A` | `app` | `cname.vercel-dns.com` (or Vercel-assigned IP) | Points frontend subdomain to Vercel |

> [!IMPORTANT]
> Verify DNS resolution before requesting TLS certificates:
> ```bash
> dig +short api.YOUR_DOMAIN.com
> dig +short app.YOUR_DOMAIN.com
> ```

---

## 3. Hostinger VPS Backend Deployment

### Step 3.1: Connect to VPS
```bash
ssh root@<YOUR_VPS_IP>
```

### Step 3.2: Provision VPS Prerequisites
Run the automated setup script to install Docker, Docker Compose, Nginx, Certbot, UFW, and initialize `/opt/resume-parser`:
```bash
curl -fsSL https://raw.githubusercontent.com/Asif259/Resume-Parser/main/scripts/setup-vps.sh | bash
```
*(Or clone the repository and run `./scripts/setup-vps.sh` directly)*

### Step 3.3: Clone Repository
```bash
mkdir -p /opt/resume-parser/app
git clone https://github.com/Asif259/Resume-Parser.git /opt/resume-parser/app
cd /opt/resume-parser/app
```

### Step 3.4: Configure Production Environment Variables
Create `/opt/resume-parser/app/.env`:
```bash
cp backend/.env.production.example /opt/resume-parser/app/.env
nano /opt/resume-parser/app/.env
```
Ensure `CORS_ORIGINS` includes your frontend URL:
```env
APP_ENV=production
PROJECT_NAME="NLP Resume Parser API"
DATABASE_URL=sqlite:////app/data/resumes.db
UPLOAD_DIR=/app/uploads
MODEL_DIR=/app/models/ner
HF_HOME=/app/cache/huggingface
FORCE_CPU=true
USE_ML=true
USE_SEMANTIC=true
CORS_ORIGINS=["https://app.YOUR_DOMAIN.com"]
RATE_LIMIT_PER_MINUTE=60
MAX_FILE_SIZE=10485760
```

### Step 3.5: Transfer Custom DistilBERT Model Artifacts
Because `model.safetensors` (253 MB) is excluded from Git, transfer it from your local machine to the VPS:
```bash
# Run this on your local machine:
./scripts/deploy-model.sh root@<YOUR_VPS_IP> 22
```
This transfers `model.safetensors`, `config.json`, `tokenizer.json`, and `calibration.json` to `/opt/resume-parser/models/ner/`.

### Step 3.6: Build and Launch Backend Container
On the VPS:
```bash
cd /opt/resume-parser/app
docker compose up -d --build
```
Verify container status:
```bash
docker compose ps
docker compose logs -f backend
```
Test internal healthcheck:
```bash
curl http://127.0.0.1:8000/health
```

---

## 4. Nginx Reverse Proxy and SSL Configuration

### Step 4.1: Install Nginx Configuration
```bash
cp /opt/resume-parser/app/deploy/nginx/resume-parser-api.conf /etc/nginx/sites-available/resume-parser-api.conf
sed -i 's/YOUR_DOMAIN.com/yourdomain.com/g' /etc/nginx/sites-available/resume-parser-api.conf

ln -s /etc/nginx/sites-available/resume-parser-api.conf /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### Step 4.2: Obtain Free Let's Encrypt TLS Certificate
```bash
certbot --nginx -d api.YOUR_DOMAIN.com --non-interactive --agree-tos -m admin@YOUR_DOMAIN.com
```

### Step 4.3: Verify Public API
```bash
curl -i https://api.YOUR_DOMAIN.com/health
```
Expected output:
```json
{
  "status": "ok",
  "project": "NLP Resume Parser API",
  "environment": "production",
  "models": {
    "spacy": "loaded",
    "distilbert_ner": "available",
    "sentence_transformers": "available"
  }
}
```

---

## 5. Next.js Frontend Deployment on Vercel

### Option A: Using Vercel Dashboard (Recommended)
1. Navigate to [vercel.com](https://vercel.com) and click **"Add New Project"**.
2. Select the GitHub repository `Asif259/Resume-Parser`.
3. Configure the project settings:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend` *(Click Edit and choose `frontend`)*
   - **Build Command**: `next build` (Default)
   - **Output Directory**: `.next` (Default)
   - **Install Command**: `npm install` (Default)
4. Add the Environment Variable:
   - Key: `NEXT_PUBLIC_API_BASE_URL`
   - Value: `https://api.YOUR_DOMAIN.com`
5. Click **Deploy**.
6. Under **Project Settings > Domains**, add your custom domain: `app.YOUR_DOMAIN.com`.

### Option B: Using Vercel CLI
```bash
cd frontend
npx vercel login
npx vercel link
npx vercel env add NEXT_PUBLIC_API_BASE_URL production
# Enter value: https://api.YOUR_DOMAIN.com
npx vercel --prod
```

---

## 6. End-to-End Verification & Smoke Tests

Run these tests against the production deployment:

1. **Health Check**:
   ```bash
   curl -s https://api.YOUR_DOMAIN.com/health | jq
   ```
2. **PDF Upload & Parsing**:
   ```bash
   curl -X POST "https://api.YOUR_DOMAIN.com/api/parse" \
     -H "Accept: application/json" \
     -F "file=@tests/fixtures/resumes/twocol_software_eng.pdf"
   ```
3. **DOCX Upload & Parsing**:
   ```bash
   curl -X POST "https://api.YOUR_DOMAIN.com/api/parse" \
     -F "file=@tests/fixtures/resumes/docx_table_qa_lead.docx"
   ```
4. **List Resumes**:
   ```bash
   curl -s https://api.YOUR_DOMAIN.com/api/resumes | jq
   ```
5. **Frontend UI Inspection**:
   - Visit `https://app.YOUR_DOMAIN.com` in your browser.
   - Go to `Settings` -> Verify backend connection status shows "FastAPI Service Operational (Healthy)".
   - Go to `Upload Resume` -> Drag and drop a test resume.
   - Verify Candidate Info, Experience timeline, Skills with category tags, and Evidence tooltips display accurately.
   - Download the parsed JSON result.

---

## 7. Automated Backups & Maintenance

### Database Backups
Daily backups run automatically via cron at 03:00 UTC using `/opt/resume-parser/scripts/backup-db.sh`.
Backups are saved as compressed archives at `/opt/resume-parser/backups/resumes_YYYYMMDD_HHMMSS.db.gz` and rotated after 30 days.

To manually trigger a backup:
```bash
/opt/resume-parser/scripts/backup-db.sh
```

### Log Rotation
Application and Nginx logs are automatically rotated daily by `/etc/logrotate.d/resume-parser`.

---

## 8. Rollback Procedures

If an update fails:
1. SSH into the VPS: `ssh root@<YOUR_VPS_IP>`
2. Run the interactive rollback utility:
   ```bash
   /opt/resume-parser/scripts/rollback.sh
   ```
   Choose:
   - `1` to revert to previous Docker image
   - `2` to restore SQLite database from a selected backup archive
   - `3` to perform a clean service restart
