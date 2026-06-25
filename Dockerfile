# Assessment Rubric Agent v0.1
# Multi-stage Docker build for production deployment

# ==================== BUILD STAGE ====================
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ==================== RUNTIME STAGE ====================
FROM python:3.12-slim

LABEL maintainer="Assessment Rubric Agent Team"
LABEL version="0.1.0"
LABEL description="Assessment Rubric Agent - Teacher Copilot for K12 PAL Platform"

WORKDIR /app

# Install runtime dependencies (for PDF generation)
RUN apt-get update && apt-get install -y \
    # WeasyPrint dependencies
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    # Fonts for PDF
    fonts-dejavu \
    fonts-dejavu-core-extra \
    fonts-droid-fallback \
    fonts-freefont-ttf \
    fonts-liberation \
    fonts-noto \
    fonts-noto-cjk \
    fonts-opensymbol \
    fonts-symbola \
    # Misc
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY src/ ./src/
COPY templates/ ./templates/
COPY config/ ./config/
COPY data/ ./data/

# Create output directories
RUN mkdir -p outputs/pdfs outputs/jsons logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV INTELLIGENCE_CSV_PATH=/app/data/semantic_intelligence.csv

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "src.assessment_rubric_agent.main:app", "--host", "0.0.0.0", "--port", "8000"]
