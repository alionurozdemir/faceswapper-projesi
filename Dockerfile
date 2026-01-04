# Multi-stage build to reduce image size
FROM python:3.10-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.10-slim

# Install runtime libraries required by OpenCV and others
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ffmpeg \
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

# DEĞİŞİKLİK: CURL komutuna '--retry 5', '-L' (follow redirects) ve '-f' (fail on error) eklendi.
# -f parametresi kritik: HTTP hatası (404/500) alırsa dosya yazmaz, hata verir.
# Böylece "InvalidProtobuf" hatasına sebep olan bozuk/HTML dosyalar oluşmaz.
# GÜNCELLEME: Hugging Face mirrorları güncellendi (crj/dl-ws ve ezioruan - public erişim için)
RUN mkdir -p /app/.assets/models && \
    echo "Downloading RetinaFace..." && \
    curl -fL --retry 5 -o /app/.assets/models/retinaface_10g.onnx https://huggingface.co/crj/dl-ws/resolve/main/retinaface_10g.onnx && \
    echo "Downloading Face Landmarker..." && \
    curl -fL --retry 5 -o /app/.assets/models/face_landmarker_68_5.onnx https://huggingface.co/crj/dl-ws/resolve/main/face_landmarker_68_5.onnx && \
    echo "Downloading 2dfan4..." && \
    curl -fL --retry 5 -o /app/.assets/models/2dfan4.onnx https://huggingface.co/crj/dl-ws/resolve/main/2dfan4.onnx && \
    echo "Downloading Inswapper (THE FACE SWAPPER)..." && \
    curl -fL --retry 5 -o /app/.assets/models/inswapper_128.onnx https://huggingface.co/ezioruan/inswapper_128.onnx/resolve/main/inswapper_128.onnx && \
    echo "Downloading ArcFace..." && \
    curl -fL --retry 5 -o /app/.assets/models/arcface_w600k_r50.onnx https://huggingface.co/crj/dl-ws/resolve/main/arcface_w600k_r50.onnx && \
    echo "Downloading GFPGAN (FACE ENHANCER)..." && \
    curl -fL --retry 5 -o /app/.assets/models/GFPGANv1.4.pth https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7860', timeout=5)" || exit 1

# Run the simplified Gradio app
CMD ["python", "simple.py"]