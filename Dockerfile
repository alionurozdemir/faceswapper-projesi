FROM python:3.10-slim

# Sistem kütüphanelerini (OpenCV ve Image işlemleri için) kuruyoruz
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dosyaları kopyala
COPY . .

# Bağımlılıkları kur
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama portunu belirt (Gradio genelde 7860 kullanır)
EXPOSE 7860

# Uygulamayı çalıştır
CMD ["python", "app.py"]
