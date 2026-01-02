# Multi-stage build ile image boyutunu küçültme
FROM python:3.10-slim as builder

# Build bağımlılıkları
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Sadece requirements.txt'i kopyala ve bağımlılıkları yükle
COPY requirements.txt .

# CPU-only versiyonları için bağımlılıkları yükle
RUN pip install --no-cache-dir --user \
    basicsr==1.4.2 \
    filetype==1.2.0 \
    gradio==3.50.2 \
    numpy==1.26.1 \
    onnx==1.15.0 \
    onnxruntime==1.16.3 \
    opencv-python==4.8.1.78 \
    psutil==5.9.6 \
    realesrgan==0.3.0 \
    torch==2.1.0 \
    --index-url https://download.pytorch.org/whl/cpu \
    tqdm==4.66.1 \
    insightface==0.7.3

# Final stage - minimal image
FROM python:3.10-slim

# Runtime bağımlılıkları
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python bağımlılıklarını builder'dan kopyala
COPY --from=builder /root/.local /root/.local

# Proje dosyalarını kopyala
COPY . .

# Model dosyalarını cache klasörüne kopyala
RUN mkdir -p .cache && \
    if [ -f checkpoints/inswapper_128.onnx ]; then \
        cp checkpoints/inswapper_128.onnx .cache/; \
    fi && \
    if [ -f cache/GFPGANv1.4.pth ]; then \
        cp cache/GFPGANv1.4.pth .cache/ || true; \
    fi

# Python path'i ayarla
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=2 \
    MKL_NUM_THREADS=2 \
    NUMEXPR_NUM_THREADS=2 \
    OPENBLAS_NUM_THREADS=2

# CPU optimizasyonları için environment variables
ENV ONNXRUNTIME_EXECUTION_PROVIDERS=CPUExecutionProvider \
    CUDA_VISIBLE_DEVICES=""

# Port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7860', timeout=5)" || exit 1

# Uygulamayı başlat
CMD ["python", "app.py"]
