# Video İndirme Sunucusu

Bu proje, YouTube, Twitter ve Instagram'dan video indirmek için kullanılan bir API sunucusudur. FastAPI kullanılarak geliştirilmiştir ve video indirme işlemlerini arka planda gerçekleştirebilir.

## Özellikler

- YouTube video indirme
- Twitter video indirme
- Instagram video indirme
- Asenkron video işleme
- RESTful API arayüzü
- Otomatik API dokümantasyonu
- İndirilen videoları listeleyebilme ve yönetebilme

## Kurulum

### Gereksinimler

- Python 3.9+
- Poetry (Bağımlılık yönetimi için)

### Poetry ile Kurulum

```bash
# Poetry'yi yükleyin (eğer yüklü değilse)
pip install poetry

# Projeyi klonlayın ve klasöre girin
# git clone <repo-url>
# cd video_indirme_sunucusu

# Bağımlılıkları yükleyin
poetry install
```

### Manuel Kurulum

```bash
# Gerekli paketleri yükleyin
pip install fastapi uvicorn pytube yt-dlp instaloader
```

## Kullanım

### API Sunucusunu Başlatma

```bash
# Poetry ile
poetry run python video_api_server.py

# Veya doğrudan Python ile
python video_api_server.py
```

Sunucu varsayılan olarak `http://0.0.0.0:8000` adresinde çalışmaya başlar.

### API Dokümantasyonu

API dokümantasyonuna erişmek için sunucu çalışırken bir web tarayıcısı üzerinden:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

adreslerine gidebilirsiniz.

### Komut Satırı Uygulaması

API'nin yanı sıra, video indirmek için doğrudan komut satırından da kullanabilirsiniz:

```bash
python video_downloader.py
```

## API Endpoints

| Endpoint | Metod | Açıklama |
|----------|-------|----------|
| `/` | GET | API durumu ve sürüm bilgisi |
| `/download/` | POST | Video indirme işlemi başlatır |
| `/status/{task_id}` | GET | İndirme durumunu kontrol eder |
| `/video/{task_id}` | GET | İndirilen videoyu döndürür |
| `/videos/` | GET | Tüm indirilen videoları listeler |
| `/videos/{filename}` | DELETE | Belirtilen videoyu siler |

### Örnek İstek ve Yanıtlar

#### Video İndirme İsteği

```json
POST /download/
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "quality": "high"
}
```

#### İndirme İsteği Yanıtı

```json
{
  "task_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "pending"
}
```

#### Durum Kontrolü

```
GET /status/3fa85f64-5717-4562-b3fc-2c963f66afa6
```

#### Durum Yanıtı

```json
{
  "task_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "completed",
  "platform": "youtube",
  "download_path": "indirilen_videolar/video.mp4",
  "percentage": 100,
  "error": null
}
```

## Proje Yapısı

```
video_indirme_sunucusu/
├── video_api_server.py    # FastAPI sunucusu
├── video_downloader.py    # Video indirme fonksiyonları
├── pyproject.toml         # Proje bağımlılıkları
├── README.md              # Bu dosya
└── indirilen_videolar/    # İndirilen videolar bu klasörde saklanır
```

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## Katkıda Bulunanlar

Henüz katkıda bulunmaya açık değildir.

## İletişim

Herhangi bir sorun veya öneri için issue açabilirsiniz.