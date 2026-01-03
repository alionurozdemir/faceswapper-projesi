# Coolify'da FaceSwapper Deployment Rehberi

Bu rehber, FaceSwapper uygulamasını Coolify platformunda CPU-only bir sunucuda nasıl deploy edeceğinizi açıklar.

## Ön Gereksinimler

- Coolify kurulumu yapılmış bir sunucu
- 8GB+ RAM
- Docker desteği
- Git repository erişimi

## Deployment Adımları

### 1. Coolify'da Yeni Resource Oluşturma

1. Coolify dashboard'una giriş yapın
2. **"Resources"** veya **"Applications"** bölümüne gidin
3. **"New Resource"** veya **"New Application"** butonuna tıklayın

### 1.1. Deployment Yöntemi Seçimi

**ÖNEMLİ:** Aşağıdaki seçeneklerden birini seçin:

#### ✅ **ÖNERİLEN: Git Based → Public Repository**
- Repository'niz public ise bu seçeneği kullanın
- Coolify Git repository'nizden Dockerfile'ı otomatik bulur ve build eder
- En kolay ve otomatik yöntem

#### ✅ **Alternatif: Git Based → Private Repository**
Repository'niz private ise:
- **GitHub App** ile bağlantı (önerilen): GitHub hesabınızı Coolify'a bağlayın
- **Deploy Key** ile bağlantı: SSH key oluşturup repository'ye ekleyin

#### ❌ **KULLANMAYIN: Docker Based → Dockerfile**
- Bu seçenek Git repository olmadan sadece Dockerfile için kullanılır
- Bizim durumumuzda Git repository kullanacağımız için uygun değil

**Seçim Yaptıktan Sonra:**
- Repository URL'nizi girin
- Branch: `main` (veya kullandığınız branch)
- Coolify otomatik olarak Dockerfile'ı bulacaktır

### 2. Git Repository Bağlantısı (Git Based seçtiyseniz)

1. **Source** bölümünde:
   - **Repository URL**: Git repository URL'nizi girin (örn: `https://github.com/alionurozdemir/faceswapper-projesi`)
   - **Branch**: `main` (veya kullandığınız branch)
   - **Dockerfile Path**: `Dockerfile` (varsayılan - Coolify otomatik bulur)

### 3. Build Ayarları

**Build Settings** bölümünde (genellikle otomatik ayarlanır):

- **Build Pack**: `Dockerfile` (otomatik algılanır)
- **Dockerfile Location**: `Dockerfile` (proje root'unda)
- **Build Command**: (boş bırakın, Dockerfile otomatik kullanılacak)

**Not:** Coolify genellikle Dockerfile'ı otomatik bulur, manuel ayar gerekmez.

### 3.1. Advanced Configuration Ayarları

**Configuration** → **Advanced** bölümünde önerilen ayarlar:

#### General Ayarları:
- ✅ **Auto Deploy**: Açık (otomatik deploy için)
- ❌ **Preview Deployments**: Kapalı (production için gerekli değil)
- ❌ **Disable Build Cache**: Kapalı (cache build süresini kısaltır)
- ✅ **Inject Build Args to Dockerfile**: Açık (environment variables için gerekli)
- ❌ **Include Source Commit in Build**: Kapalı (opsiyonel)
- ✅ **Force Https**: Açık (güvenlik için)
- ✅ **Enable Gzip Compression**: Açık (performans için)
- ✅ **Strip Prefixes**: Açık (URL routing için)

#### Git Ayarları:
- ✅ **Submodules**: Açık (eğer submodule kullanıyorsanız)
- ✅ **LFS**: Açık (model dosyaları için önemli - büyük dosyalar için)
- ✅ **Shallow Clone**: Açık (daha hızlı clone için)

#### GPU Ayarları:
- ❌ **Enable GPU**: KAPALI (CPU-only sunucu için mutlaka kapalı olmalı)

**Önemli:** Build timeout ayarı bu sayfada görünmüyorsa, muhtemelen:
- Coolify'ın daha yeni versiyonlarında farklı bir yerde olabilir
- Veya varsayılan timeout yeterli olabilir
- Build timeout sorunu yaşıyorsanız, Dockerfile optimizasyonları yeterli olabilir

### 4. Environment Variables (Ortam Değişkenleri)

**Environment Variables** bölümüne şunları ekleyin:

```
OMP_NUM_THREADS=2
MKL_NUM_THREADS=2
NUMEXPR_NUM_THREADS=2
OPENBLAS_NUM_THREADS=2
ONNXRUNTIME_EXECUTION_PROVIDERS=CPUExecutionProvider
CUDA_VISIBLE_DEVICES=
PYTHONUNBUFFERED=1
```

### 5. Resource Limits (Kaynak Sınırları)

**Resource Limits** bölümünde 8GB RAM için:

```
Memory Limit: 7GB (7168 MB)
Memory Swap: 7GB (7168 MB)
CPU Limit: 4 cores (veya mevcut CPU sayısına göre)
```

**Not**: Sistemin kendisi için en az 1GB RAM bırakın.

### 6. Port Ayarları

**Port Configuration**:

```
Port: 7860
Protocol: HTTP
```

### 7. Health Check (Opsiyonel)

Coolify otomatik health check yapabilir, ancak manuel ayarlamak isterseniz:

```
Health Check Path: /
Health Check Port: 7860
Health Check Interval: 30s
```

### 8. Deployment

1. Tüm ayarları kontrol edin
2. **"Deploy"** veya **"Save & Deploy"** butonuna tıklayın
2. İlk build işlemi biraz zaman alabilir (5-10 dakika)
3. Logları takip ederek build sürecini izleyebilirsiniz

## Deployment Sonrası Kontroller

### 1. Log Kontrolü

Coolify dashboard'unda **"Logs"** bölümünden uygulamanın çalışıp çalışmadığını kontrol edin:

```bash
# Başarılı başlangıç logları şunları içermelidir:
# - "Running on local URL: http://0.0.0.0:7860"
# - Model dosyalarının yüklendiğine dair mesajlar
```

### 2. Uygulama Erişimi

Deployment tamamlandıktan sonra:

- Coolify otomatik olarak bir domain atayacaktır
- Veya manuel olarak domain ekleyebilirsiniz
- Uygulama `http://your-domain:7860` adresinde erişilebilir olmalıdır

### 3. Performans İzleme

**Monitoring** bölümünden:
- CPU kullanımını
- RAM kullanımını
- Disk kullanımını
- Network trafiğini

izleyebilirsiniz.

## Sorun Giderme

### Problem: Build Başarısız Oluyor

**Çözüm**:
- Logları kontrol edin
- Model dosyalarının (`cache/inswapper_128.onnx`, `cache/GFPGANv1.4.pth`) repository'de olduğundan emin olun
- Dockerfile'daki path'leri kontrol edin

### Problem: Uygulama Başlamıyor / Crash Oluyor

**Çözüm**:
- Memory limit'i artırın (7GB → 6GB)
- CPU thread sayısını azaltın (OMP_NUM_THREADS=1)
- Logları detaylı inceleyin

### Problem: "Minimum memory limit allowed is 6MB" Hatası

**Hata:** `Error response from daemon: Minimum memory limit allowed is 6MB`

**Neden:** Resource Limits'te ayarlanan memory limit değeri doğru uygulanmamış veya çok düşük bir değer girilmiş.

**Çözüm:**
1. **Resource Limits** bölümüne gidin
2. **Maximum Memory Limit** alanını kontrol edin:
   - Değer **MB cinsinden** girilmelidir (örn: `7168` = 7GB)
   - **GB cinsinden değil** (örn: `7` veya `7GB` yazmayın)
   - Minimum değer: `6144` (6GB) veya daha yüksek
3. **Soft Memory Limit** değerini de kontrol edin (örn: `6144`)
4. **Save** butonuna tıklayın
5. **Redeploy** yapın

**Doğru Değerler (8GB RAM sunucu için):**
- Soft Memory Limit: `6144` (MB)
- Maximum Memory Limit: `7168` (MB)
- Maximum Swap Limit: `0` (MB)

**Not:** Eğer ayarlar doğru görünüyorsa ama hata devam ediyorsa:
- Coolify'ın bu ayarları Docker Compose'a aktarmadığı bir bug olabilir
- **Save** butonuna tıklayıp tekrar kontrol edin
- Coolify'ı yeniden başlatmayı deneyin
- Veya Resource Limits'i silip tekrar ekleyin

### Problem: Yavaş Performans

**Çözüm**:
- CPU core sayısını artırın
- Memory limit'i optimize edin
- Thread sayılarını CPU core sayısına göre ayarlayın

### Problem: Port Erişim Sorunu

**Çözüm**:
- Coolify'ın port mapping ayarlarını kontrol edin
- Firewall kurallarını kontrol edin
- Reverse proxy ayarlarını kontrol edin

### Problem: Build Timeout / Gateway Timeout (504)

**Build Timeout Çözümü**:
- Application Settings → Advanced bölümünde "Build Timeout" değerini artırın (örn: 30 dakika → 60 dakika)
- Memory limit'i kontrol edin (build sırasında yeterli RAM olduğundan emin olun)

**Gateway Timeout (504) Çözümü**:

Coolify dokümantasyonuna göre ([Gateway Timeout Troubleshooting](https://coolify.io/docs/troubleshoot/applications/gateway-timeout)):

#### Traefik Proxy (Varsayılan) İçin:

1. **Servers** → **[YourServer]** → **Proxy** bölümüne gidin
2. **Command** bölümüne şu ayarları ekleyin:

```yaml
command:
  - "--entrypoints.https.transport.respondingTimeouts.readTimeout=5m"
  - "--entrypoints.https.transport.respondingTimeouts.writeTimeout=5m"
  - "--entrypoints.https.transport.respondingTimeouts.idleTimeout=5m"
```

Bu ayarlar 5 dakikalık timeout sağlar. İhtiyacınıza göre artırabilirsiniz (örn: `10m`, `15m`).

#### Caddy Proxy İçin:

Application'ın **Container Labels** bölümüne şu label'ları ekleyin:

```yaml
caddy.servers.timeouts.read_body=300s
caddy.servers.timeouts.read_header=300s
caddy.servers.timeouts.write=300s
caddy.servers.timeouts.idle=5m
```

**Not**: Caddy varsayılan olarak timeout'suz çalışır, bu yüzden genellikle timeout sorunu yaşanmaz.

#### Önemli Notlar:

- **Build timeout** ve **Gateway timeout** farklı şeylerdir:
  - **Build timeout**: Docker build işleminin ne kadar sürebileceği
  - **Gateway timeout**: Uygulamanın HTTP isteklerine ne kadar sürede cevap vermesi gerektiği
- FaceSwapper gibi AI uygulamaları için uzun işlem süreleri normaldir, timeout'ları buna göre ayarlayın
- Büyük dosya upload'ları için chunked upload implementasyonu düşünülebilir

## Optimizasyon İpuçları

### 1. Model Dosyalarını Optimize Etme

Model dosyaları büyük olduğu için:
- İlk deployment'ta indirme süresi uzun olabilir
- Model dosyalarını repository'de tutmak yerine, build sırasında indirmeyi tercih edebilirsiniz

### 2. Cache Kullanımı

Coolify'ın build cache özelliğini kullanarak:
- Sonraki deployment'lar daha hızlı olacaktır
- Sadece değişen dosyalar yeniden build edilecektir

### 3. Resource Monitoring

Düzenli olarak:
- CPU ve RAM kullanımını izleyin
- Gerekirse resource limit'leri ayarlayın
- Peak saatlerde performansı gözlemleyin

## Örnek Coolify YAML Konfigürasyonu

Eğer Coolify YAML formatı kullanıyorsanız:

```yaml
version: '3.8'

services:
  faceswapper:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "7860:7860"
    environment:
      - OMP_NUM_THREADS=2
      - MKL_NUM_THREADS=2
      - NUMEXPR_NUM_THREADS=2
      - OPENBLAS_NUM_THREADS=2
      - ONNXRUNTIME_EXECUTION_PROVIDERS=CPUExecutionProvider
      - CUDA_VISIBLE_DEVICES=
      - PYTHONUNBUFFERED=1
    deploy:
      resources:
        limits:
          memory: 7G
          cpus: '4'
        reservations:
          memory: 4G
          cpus: '2'
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:7860', timeout=5)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
```

## İletişim ve Destek

Sorun yaşarsanız:
1. Coolify loglarını kontrol edin
2. Docker container loglarını inceleyin
3. GitHub Issues'da sorun bildirin

## Notlar

- İlk başlatmada model dosyaları yükleneceği için biraz zaman alabilir
- CPU-only modda işlem süreleri GPU'ya göre daha uzun olacaktır
- 8GB RAM yeterli olmalıdır, ancak yoğun kullanımda izleme yapın
- Model dosyaları cache'lenir, sonraki istekler daha hızlı olacaktır

---

## Bu Konuşmada Yapılan Değişiklikler ve Optimizasyonlar

Bu bölüm, FaceSwapper projesinin CPU-only Ubuntu sunucuda Docker ile çalıştırılması için yapılan tüm optimizasyonları ve düzeltmeleri içerir. Bu bilgiler, gelecekte benzer bir deployment yapılırken referans olarak kullanılabilir.

### 1. Dockerfile Optimizasyonu

**Başlangıç Durumu:**
- Basit Dockerfile, GPU bağımlılıkları içeriyordu
- `libgl1-mesa-glx` paketi kullanılıyordu (Debian trixie'de mevcut değil)
- Tüm paketler tek seferde yükleniyordu (timeout riski)

**Yapılan Değişiklikler:**

#### a) Multi-Stage Build
- İki aşamalı build yapısı oluşturuldu:
  - **Builder stage**: Build bağımlılıkları ve Python paketleri
  - **Final stage**: Minimal runtime image
- Image boyutu küçültüldü

#### b) Debian Trixie Uyumluluğu
- `libgl1-mesa-glx` → `libgl1` (yeni Debian versiyonunda mevcut)
- `FROM ... as builder` → `FROM ... AS builder` (büyük harf uyarısı düzeltildi)

#### c) PyTorch CPU Versiyonu
- PyTorch CPU wheel repository'si eklendi
- `--extra-index-url https://download.pytorch.org/whl/cpu` kullanıldı
- **Önemli:** `--index-url` yerine `--extra-index-url` kullanıldı (PyPI + PyTorch repo desteği)

#### d) Paketlerin Aşamalı Yüklenmesi
Build timeout riskini azaltmak için paketler gruplara ayrıldı:
1. Temel paketler: `numpy`, `filetype`, `psutil`, `tqdm`
2. PyTorch CPU: `torch==2.1.0`
3. ONNX paketleri: `onnx`, `onnxruntime`
4. OpenCV: `opencv-python`
5. Büyük paketler: `basicsr`, `gradio`, `realesrgan`, `insightface`

**Sonuç:** Her aşama ayrı cache'lenir, build timeout riski azalır.

### 2. Requirements.txt Güncellemesi

**Değişiklik:**
- `onnxruntime-gpu==1.16.3` → `onnxruntime==1.16.3` (CPU versiyonu)

**Neden:** GPU bağımlılığı kaldırıldı, CPU-only sunucu için uygun hale getirildi.

### 3. Kod Optimizasyonları

#### a) simple.py
- `provider = 'cuda'` → `provider = 'cpu'`
- FaceFusion CLI için CPU execution provider kullanılıyor

#### b) predict.py
- `device = 'cuda' if torch.cuda.is_available() else 'mps'` → `device = 'cpu'`
- CPU-only sunucu için optimize edildi

### 4. .dockerignore Dosyası

Yeni dosya oluşturuldu:
- Gereksiz dosyalar build'e dahil edilmiyor
- Build context boyutu küçültüldü
- Build süresi azaldı

### 5. Coolify Deployment Konfigürasyonu

#### a) Git Based Deployment
- **Seçilen Yöntem:** Git Based → Public Repository
- Repository: `https://github.com/alionurozdemir/faceswapper-projesi`
- Branch: `main`
- Dockerfile otomatik algılanıyor

#### b) Environment Variables
Aşağıdaki environment variables eklendi:
```
OMP_NUM_THREADS=2
MKL_NUM_THREADS=2
NUMEXPR_NUM_THREADS=2
OPENBLAS_NUM_THREADS=2
ONNXRUNTIME_EXECUTION_PROVIDERS=CPUExecutionProvider
CUDA_VISIBLE_DEVICES= (boş)
PYTHONUNBUFFERED=1
```

**Not:** `CUDA_VISIBLE_DEVICES` değeri boş bırakılmalı (hiçbir şey yazılmamalı).

#### c) Resource Limits (4 VCPU, 8GB RAM Sunucu İçin)
- **Number of CPUs:** `4`
- **CPU sets:** `0-3` (veya boş)
- **CPU Weight:** `1024` (varsayılan)
- **Soft Memory Limit:** `6144` MB (6GB)
- **Swappiness:** `60` (varsayılan)
- **Maximum Memory Limit:** `7168` MB (7GB)
- **Maximum Swap Limit:** `0` (swap kullanılmıyor)

#### d) Advanced Configuration
- ✅ **Auto Deploy:** Açık
- ❌ **Preview Deployments:** Kapalı
- ❌ **Disable Build Cache:** Kapalı (cache build süresini kısaltır)
- ✅ **Inject Build Args to Dockerfile:** Açık
- ✅ **LFS:** Açık (model dosyaları için önemli)
- ✅ **Shallow Clone:** Açık (daha hızlı)
- ❌ **Enable GPU:** KAPALI (CPU-only için kritik)

### 6. Timeout Ayarları

#### a) Build Timeout
- Advanced Configuration sayfasında görünmüyor
- Dockerfile optimizasyonları ile timeout riski azaltıldı
- Paketlerin aşamalı yüklenmesi ile build süresi optimize edildi

#### b) Gateway Timeout (504)
Coolify dokümantasyonuna göre ([Gateway Timeout Troubleshooting](https://coolify.io/docs/troubleshoot/applications/gateway-timeout)):

**Traefik Proxy için:**
Server → Proxy → Command bölümüne eklenecek:
```yaml
command:
  - "--entrypoints.https.transport.respondingTimeouts.readTimeout=5m"
  - "--entrypoints.https.transport.respondingTimeouts.writeTimeout=5m"
  - "--entrypoints.https.transport.respondingTimeouts.idleTimeout=5m"
```

**Caddy Proxy için:**
Application Container Labels'e eklenecek:
```yaml
caddy.servers.timeouts.read_body=300s
caddy.servers.timeouts.read_header=300s
caddy.servers.timeouts.write=300s
caddy.servers.timeouts.idle=5m
```

### 7. Karşılaşılan Sorunlar ve Çözümleri

#### Sorun 1: `libgl1-mesa-glx` Paketi Bulunamadı
**Hata:** `E: Package 'libgl1-mesa-glx' has no installation candidate`
**Çözüm:** `libgl1-mesa-glx` → `libgl1` (Debian trixie uyumluluğu)

#### Sorun 2: `basicsr` Paketi PyTorch Repository'sinde Bulunamadı
**Hata:** `ERROR: Could not find a version that satisfies the requirement basicsr==1.4.2`
**Çözüm:** `--index-url` → `--extra-index-url` (PyPI + PyTorch repo desteği)

#### Sorun 3: Build Timeout
**Hata:** Build işlemi timeout oluyor, exit code 255
**Çözüm:** Paketler aşamalı yüklenmeye başlandı (5 aşamaya bölündü)

### 8. Git İşlemleri

Tüm değişiklikler GitHub'a push edildi:
- Dockerfile optimizasyonları
- requirements.txt güncellemesi
- simple.py ve predict.py CPU optimizasyonları
- .dockerignore eklenmesi
- COOLIFY_DEPLOYMENT.md rehberi oluşturulması ve güncellemeleri

### 9. Son Durum

**Başarılı Olması Gereken Yapılandırma:**
- ✅ CPU-only optimizasyonu tamamlandı
- ✅ Dockerfile multi-stage build ile optimize edildi
- ✅ Paketler aşamalı yükleniyor (timeout riski azaltıldı)
- ✅ Environment variables ayarlandı
- ✅ Resource limits optimize edildi
- ✅ Advanced Configuration önerileri uygulandı

**Beklenen Sonuç:**
- Build başarılı olmalı
- Uygulama CPU-only sunucuda çalışmalı
- Port 7860'da erişilebilir olmalı
- Model dosyaları cache'lenmeli

### 10. Gelecek Referans İçin Notlar

Bu deployment sürecinde öğrenilen önemli noktalar:

1. **Debian Trixie Uyumluluğu:** Yeni Debian versiyonlarında paket isimleri değişebilir
2. **PyTorch CPU Installation:** `--extra-index-url` kullanılmalı, `--index-url` değil
3. **Build Timeout:** Büyük paketler için aşamalı yükleme stratejisi kullanılmalı
4. **CPU-only Deployment:** Tüm GPU referansları kaldırılmalı (kod, environment variables, Dockerfile)
5. **Coolify Configuration:** Advanced ayarlarda GPU mutlaka kapalı olmalı
6. **Resource Limits:** 8GB RAM için 7GB limit, 1GB sistem için ayrılmalı

Bu bilgiler, benzer bir deployment yapılırken veya sorun giderme sırasında referans olarak kullanılabilir.

