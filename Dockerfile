# Multi-stage build to reduce image size
FROM python:3.10-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Install dependencies into a user directory to easily copy later
# Using --extra-index-url to prioritize CPU wheels for PyTorch
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.10-slim

# Install runtime libraries required by OpenCV and others
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed python packages from builder
COPY --from=builder /root/.local /root/.local

# Add the local bin to PATH
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Set environment variables for CPU optimization
ENV OMP_NUM_THREADS=2 \
    MKL_NUM_THREADS=2 \
    NUMEXPR_NUM_THREADS=2 \
    OPENBLAS_NUM_THREADS=2 \
    ONNXRUNTIME_EXECUTION_PROVIDERS=CPUExecutionProvider \
    PYTHONUNBUFFERED=1

# Expose the application port
EXPOSE 7860

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7860', timeout=5)" || exit 1

# Run the simplified Gradio app
CMD ["python", "simple.py"]
