FROM python:3.10-slim

# Sistem kütüphanelerini güncel paket isimleriyle kuruyoruz
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dosyaları kopyala
COPY . .

# Modeli kodun beklediği gizli klasöre kopyala
RUN mkdir -p .cache && cp checkpoints/inswapper_128.onnx .cache/

# Bağımlılıkları kur (Ağır kütüphaneler olduğu için timeout süresini artırıyoruz)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 7860

CMD ["python", "app.py"]
