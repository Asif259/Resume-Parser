# Production Dockerfile for NLP Resume Parser Backend
FROM python:3.13-slim AS runner

# 1. Install system runtime dependencies (Tesseract OCR, PyMuPDF, image rendering, curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Configure Python environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app:/app/backend \
    APP_ENV=production \
    FORCE_CPU=true \
    HF_HOME=/app/cache/huggingface \
    MODEL_DIR=/app/models/ner \
    DATABASE_URL=sqlite:////app/data/resumes.db \
    UPLOAD_DIR=/app/uploads

WORKDIR /app

# 3. Create non-root user and persistent directory structure
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/bash -m appuser && \
    mkdir -p /app/data /app/uploads /app/models/ner /app/cache/huggingface && \
    chown -R appuser:appuser /app

# 4. Install PyTorch CPU wheel first to prevent downloading heavy CUDA dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch>=2.2.0 --index-url https://download.pytorch.org/whl/cpu

# 5. Copy and install backend requirements
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 6. Pre-download spaCy model and pre-cache Sentence Transformer to eliminate runtime latency
RUN python -m spacy download en_core_web_sm && \
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')" && \
    chown -R appuser:appuser /app/cache

# 7. Copy application code and schemas
COPY backend/app /app/app
COPY backend/run.py /app/run.py
COPY tools /app/tools
COPY backend/entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/health || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

