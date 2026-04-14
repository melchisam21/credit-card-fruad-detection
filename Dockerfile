# ── Stage 1: builder ─────────────────────────────────────────────────────────
# Use a slim Python image to keep the final layer small.
FROM python:3.11-slim AS builder

WORKDIR /install

# Copy and install dependencies into an isolated directory.
# This layer is cached unless requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install/deps -r requirements.txt


# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Non-root user for security best practice
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install/deps /usr/local

# Copy application source code
COPY app/        ./app/
COPY models/     ./models/

# Create the logs directory with appropriate permissions
RUN mkdir -p logs && chown -R appuser:appgroup /app

USER appuser

# Expose the port uvicorn will bind to
EXPOSE 8000

# Health check — Docker will restart the container if the API goes down
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Start: 1 worker is correct for a single GPU/single-model service.
# Scale horizontally with multiple replicas instead.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
