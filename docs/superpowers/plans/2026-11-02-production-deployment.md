# Production Deployment Implementation Plan: NLP-Based Resume Parser

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy the existing NLP-based Resume Parser application to production with Next.js frontend on Vercel and FastAPI backend on Hostinger VPS using Docker, Nginx, HTTPS, and persistent storage for SQLite, uploaded resumes, and ML models.

**Architecture:** The Next.js frontend is hosted on Vercel (`app.YOUR_DOMAIN.com`) and communicates via HTTPS REST APIs with the FastAPI backend on a Hostinger VPS (`api.YOUR_DOMAIN.com`). The backend runs in a hardened Docker container behind an Nginx reverse proxy with Certbot TLS, utilizing persistent host volumes for SQLite database (`resumes.db`), uploaded files (`uploads/`), and the custom DistilBERT NER and Sentence Transformers models (`models/ner/`, Hugging Face cache).

**Tech Stack:** Next.js 16.4.3, React 19.3.0, TypeScript 5, Tailwind CSS 4, Python 3.13, FastAPI, Pydantic v2, SQLAlchemy 2.0, SQLite 3, PyTorch CPU, Hugging Face Transformers (DistilBERT), spaCy 3.8 (`en_core_web_sm`), Sentence Transformers (`all-MiniLM-L6-v2`), PyMuPDF, Tesseract OCR, Docker & Docker Compose, Nginx, Certbot (Let's Encrypt).

**Spec:** MASTER PROMPT: Production Deployment of NLP-Based Resume Parser

## Global Constraints
- Preserve all existing 125 tests; zero test regressions.
- Preserve existing API response contracts and endpoints (`/health`, `/api/parse`, `/api/resumes`, `/api/resumes/{id}`).
- Backend ML models (DistilBERT, spaCy, Sentence Transformers) and OCR (Tesseract, PyMuPDF) must run on CPU in production without GPU/CUDA bloat.
- Persistent directories on VPS: `/opt/resume-parser/data`, `/opt/resume-parser/uploads`, `/opt/resume-parser/models/ner`, `/opt/resume-parser/cache/huggingface`, `/opt/resume-parser/backups`.
- No sensitive keys, passwords, or PII logged or committed to Git.
- Internal backend port 8000 must only bind to `127.0.0.1` and never be publicly exposed.
- All file uploads capped at 10 MB with content/magic-byte validation.

## Review Focus
1. `models/ner/model.safetensors` is in `.gitignore` (253MB) and will not be transferred via git clone on VPS — plan must have an explicit transfer mechanism.
2. In `backend/app/ml/config.py`, `PROJECT_ROOT` uses `parents[3]` which breaks if backend runs in an isolated directory unless `MODEL_DIR` is environment-configurable and `tools.annotation_schema` has a fallback.
3. `/health` endpoint must distinguish basic API health and model readiness without breaking existing test assertions that check `{"status": "ok", "project": ...}`.
4. Nginx `client_max_body_size` must be set to 12M (above 10M upload cap) and proxy timeouts to 180s to prevent 413 or 504 timeouts during transformer OCR/parsing.
5. SQLite backups must use the online `.backup` API rather than raw file copying to avoid database corruption under concurrent transactions.

---

### Task 1: Backend and Frontend Configuration Hardening

**Files:**
- Modify: `backend/app/config.py`
- Modify: `backend/app/ml/config.py`
- Modify: `backend/app/routes/parse.py`
- Modify: `backend/app/main.py`
- Modify: `frontend/lib/api.ts`
- Modify: `frontend/app/settings/page.tsx`
- Test: `tests/test_api.py`, `tests/test_scaffold.py`, `tests/test_ml_pipeline.py`

**Interfaces:**
- Consumes: `Settings` in `backend/app/config.py`, `MODEL_DIR` in `backend/app/ml/config.py`
- Produces: Environment-driven `MODEL_DIR`, `DATABASE_URL`, `UPLOAD_DIR`, `USE_ML`, `USE_SEMANTIC`, `CORS_ORIGINS`; dual-env frontend API target resolution.

- [ ] **Step 1: Write unit tests verifying environment configuration overrides**
Add test in `tests/test_config.py` testing `MODEL_DIR` override, `USE_ML` toggle, and dual CORS origin list parsing.

- [ ] **Step 2: Run test to verify it fails before modification**
Run: `pytest tests/test_config.py -v`

- [ ] **Step 3: Update `backend/app/config.py` and `backend/app/ml/config.py`**
Allow `DATABASE_URL`, `UPLOAD_DIR`, `MODEL_DIR`, `USE_ML` (default `True`), and `USE_SEMANTIC` (default `True`) to be overridden via environment variables. Add resilient fallback for `tools.annotation_schema.BIO_TAGS` in `backend/app/ml/config.py`.

- [ ] **Step 4: Update `backend/app/routes/parse.py` and `backend/app/main.py`**
In `backend/app/routes/parse.py`, pass `use_ml=settings.USE_ML, use_semantic=settings.USE_SEMANTIC` to `parse_resume()`. In `backend/app/main.py`, include model readiness status in `/health` payload while maintaining `status="ok"` and `project=settings.PROJECT_NAME`.

- [ ] **Step 5: Update `frontend/lib/api.ts` and `frontend/app/settings/page.tsx`**
Support both `process.env.NEXT_PUBLIC_API_BASE_URL` and `process.env.NEXT_PUBLIC_API_URL` gracefully.

- [ ] **Step 6: Run existing pytest suite and frontend build to verify zero regressions**
Run: `pytest` and `cd frontend && npm run build`

- [ ] **Step 7: Commit configuration hardening changes**
```bash
git add backend/app frontend/lib frontend/app tests/
git commit -m "feat(config): support production environment overrides and dual-env frontend API target"
```

---

### Task 2: Production Dockerfile and .dockerignore

**Files:**
- Create: `backend/Dockerfile`
- Create: `backend/.dockerignore`
- Create: `backend/entrypoint.sh`

**Interfaces:**
- Consumes: `backend/requirements.txt`, Python 3.13-slim, system packages (`tesseract-ocr`, `libgl1`)
- Produces: Production Docker container image with CPU-only PyTorch, pre-cached spaCy model, internal port 8000 exposure, non-root user execution, and healthcheck.

- [ ] **Step 1: Write `backend/Dockerfile`**
Multi-stage or optimized single-stage build using `python:3.13-slim`:
  - Install runtime dependencies: `tesseract-ocr`, `tesseract-ocr-eng`, `libgl1-mesa-glx` / `libglib2.0-0`, `curl`.
  - Install CPU-only PyTorch wheel (`torch>=2.2.0 --index-url https://download.pytorch.org/whl/cpu`).
  - Install `requirements.txt`.
  - Pre-download spaCy `en_core_web_sm` model.
  - Pre-cache SentenceTransformers `all-MiniLM-L6-v2` tokenizer/weights during image build to eliminate first-request latency.
  - Create non-root `appuser` (UID 1000) and directories `/app/data`, `/app/uploads`, `/app/models/ner`, `/app/cache/huggingface`.
  - Configure `HEALTHCHECK --interval=30s --timeout=5s --start-period=30s CMD curl -f http://localhost:8000/health || exit 1`.
  - Set entrypoint / CMD: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1`.

- [ ] **Step 2: Write `backend/.dockerignore` and `.dockerignore`**
Exclude `.git`, `.venv`, `__pycache__`, `.pytest_cache`, `tests`, `*.db`, `node_modules`, `frontend`, `.next`, `uploads/*`, `!uploads/.gitkeep`, `models/**/*.safetensors`.

- [ ] **Step 3: Write `backend/entrypoint.sh`**
Verify environment variables, directory permissions, and launch uvicorn safely.

- [ ] **Step 4: Verify Dockerfile syntax and consistency**
Inspect and lint Dockerfile.

- [ ] **Step 5: Commit backend containerization files**
```bash
git add backend/Dockerfile backend/.dockerignore backend/entrypoint.sh
git commit -m "feat(docker): create production Dockerfile and ignore rules for backend"
```

---

### Task 3: Production Docker Compose and Service Configuration

**Files:**
- Create: `docker-compose.yml`
- Create: `backend/.env.production.example`
- Create: `frontend/.env.production.example`

**Interfaces:**
- Consumes: Backend Docker image, Hostinger VPS persistent host directories
- Produces: One-command production deployment with persistent volumes and healthchecks.

- [ ] **Step 1: Write `docker-compose.yml`**
Define `backend` service:
  - `image: resume-parser-backend:latest` (or `build: { context: ., dockerfile: backend/Dockerfile }`)
  - `restart: unless-stopped`
  - `ports: ["127.0.0.1:8000:8000"]` (bound strictly to localhost)
  - `volumes`:
    - `/opt/resume-parser/data:/app/data`
    - `/opt/resume-parser/uploads:/app/uploads`
    - `/opt/resume-parser/models/ner:/app/models/ner`
    - `/opt/resume-parser/cache/huggingface:/app/cache/huggingface`
  - `environment`:
    - `APP_ENV=production`
    - `DATABASE_URL=sqlite:////app/data/resumes.db`
    - `UPLOAD_DIR=/app/uploads`
    - `MODEL_DIR=/app/models/ner`
    - `HF_HOME=/app/cache/huggingface`
    - `CORS_ORIGINS=["https://app.YOUR_DOMAIN.com"]`
    - `USE_ML=true`
    - `USE_SEMANTIC=true`
    - `RATE_LIMIT_PER_MINUTE=60`
  - `healthcheck` definition.

- [ ] **Step 2: Write environment templates**
Create `backend/.env.production.example` and `frontend/.env.production.example` with documented variables and placeholders.

- [ ] **Step 3: Commit Docker Compose and environment templates**
```bash
git add docker-compose.yml backend/.env.production.example frontend/.env.production.example
git commit -m "feat(compose): add production docker-compose service definition and env templates"
```

---

### Task 4: Nginx Reverse Proxy and Security Configuration

**Files:**
- Create: `deploy/nginx/resume-parser-api.conf`
- Create: `deploy/nginx/security-headers.conf`

**Interfaces:**
- Consumes: Port 80/443 public traffic on `api.YOUR_DOMAIN.com`
- Produces: Secure reverse proxy forwarding to `127.0.0.1:8000` with 12M body size, 180s timeouts, security headers, and Certbot ACME challenge support.

- [ ] **Step 1: Write Nginx site configuration `deploy/nginx/resume-parser-api.conf`**
Include:
  - `server_name api.YOUR_DOMAIN.com;`
  - `client_max_body_size 12m;`
  - `proxy_read_timeout 180s;`
  - `proxy_connect_timeout 60s;`
  - `proxy_send_timeout 180s;`
  - Proxy headers (`Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`).
  - Strict security headers (`X-Frame-Options DENY`, `X-Content-Type-Options nosniff`, `Referrer-Policy "strict-origin-when-cross-origin"`).
  - Rate limiting zone configuration (`limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;`).
  - Support for Certbot ACME challenge (`/.well-known/acme-challenge/`).

- [ ] **Step 2: Commit Nginx configurations**
```bash
git add deploy/nginx/
git commit -m "feat(nginx): add production reverse proxy configuration with security headers"
```

---

### Task 3: Hostinger VPS Setup, Model Transfer, and SQLite Backup Scripts

**Files:**
- Create: `scripts/setup-vps.sh`
- Create: `scripts/deploy-model.sh`
- Create: `scripts/backup-db.sh`
- Create: `scripts/rollback.sh`

**Interfaces:**
- Consumes: VPS SSH access, SQLite database at `/opt/resume-parser/data/resumes.db`
- Produces: Automated server initialization, safe model weights transfer, automated zero-downtime backups, and quick rollback script.

- [ ] **Step 1: Write `scripts/setup-vps.sh`**
Automate:
  - Ubuntu package updates.
  - Installation of Docker, docker-compose plugin, Nginx, Certbot, UFW, sqlite3.
  - UFW rules (`ufw allow OpenSSH`, `ufw allow 'Nginx Full'`, `ufw enable`).
  - Creation of `/opt/resume-parser/{data,uploads,models/ner,cache/huggingface,backups,logs,scripts}`.
  - Setting permissions (`chmod 750`).

- [ ] **Step 2: Write `scripts/deploy-model.sh`**
Syncs local `models/ner/` files (including the 253MB `model.safetensors` and `config.json`, `tokenizer.json`, `calibration.json`) to the VPS target directory `/opt/resume-parser/models/ner/` via SCP/rsync.

- [ ] **Step 3: Write `scripts/backup-db.sh`**
Uses SQLite's `.backup` command (`sqlite3 /opt/resume-parser/data/resumes.db ".backup /opt/resume-parser/backups/resumes_$(date +%Y%m%d_%H%M%S).db"`), compresses with gzip, verifies backup size, prunes backups older than 30 days, and logs results.

- [ ] **Step 4: Write `scripts/rollback.sh`**
Provides fast rollback to previous Docker image and restores SQLite database backup if a failure occurs.

- [ ] **Step 5: Commit deployment scripts**
```bash
git add scripts/
git commit -m "feat(ops): add VPS provisioning, model deployment, backup, and rollback scripts"
```

---

### Task 6: Documentation and Deployment Runbook

**Files:**
- Create: `DEPLOYMENT.md`

**Interfaces:**
- Consumes: Entire architecture, DNS records, Hostinger VPS guide, Vercel instructions
- Produces: Complete step-by-step production runbook with DNS tables, Certbot commands, Vercel configuration, smoke test instructions, and maintenance guide.

- [ ] **Step 1: Write `DEPLOYMENT.md`**
Document:
  - Architecture overview and topology.
  - DNS requirements (A record for `api.`, CNAME/A for `app.`).
  - Hostinger VPS setup instructions using `scripts/setup-vps.sh`.
  - Transferring model weights with `scripts/deploy-model.sh`.
  - Launching backend with `docker compose up -d --build`.
  - Setting up SSL with `certbot --nginx -d api.YOUR_DOMAIN.com`.
  - Deploying frontend to Vercel (Root Directory: `frontend`, `NEXT_PUBLIC_API_BASE_URL`).
  - Production smoke testing procedures (PDF, DOCX, OCR, retrieval).
  - Backup & restore procedures.
  - Rollback instructions.

- [ ] **Step 2: Run all tests and validation commands**
Run: `pytest` and `cd frontend && npm run build` to confirm 100% passing state.

- [ ] **Step 3: Commit documentation**
```bash
git add DEPLOYMENT.md
git commit -m "docs: add comprehensive production deployment runbook and verification procedures"
```
