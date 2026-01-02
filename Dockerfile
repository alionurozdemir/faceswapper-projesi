FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dosyaları kopyala
COPY . .

# Modeli kodun beklediği gizli klasöre kopyala
RUN mkdir -p .cache && cp checkpoints/inswapper_128.onnx .cache/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 7860

CMD ["python", "app.py"]
