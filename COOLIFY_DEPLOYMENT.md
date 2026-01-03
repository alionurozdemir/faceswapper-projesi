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

