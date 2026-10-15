# 🎮 SAYI KÂŞİFLERİ CANLI — 6. SINIF MATEMATİK YARIŞMASI

Çarpanlar, katlar ve asal sayılar konusunda öğretmen yönetiminde **canlı ve çok oyunculu** bilgi yarışması. Öğrenciler kendi telefonları ve mobil internetleri ile QR kod / 6 haneli PIN üzerinden katılabilir.

## Bağımsız öğretmen kurulumu

**📘 [ÖĞRETMEN KURULUM REHBERİ — OGRETMEN_KURULUM.md](OGRETMEN_KURULUM.md)**

Bu projenin dosyalarını kendi GitHub deponuza kopyalayıp kendi Render hesabınızda yayımladığınızda başkasının hesabına bağımlı olmazsınız.

### GitHub / Render ayarları

- GitHub: Yeni depo açın; klasör yapısını koruyarak dosyaları yükleyin.
- Render: **New → Web Service** (Static Site değil).
- Runtime: **Python**
- Build Command: `pip install -r requirements.txt`
- Start Command: `python app.py`
- Root Directory: boş
- Free plan: kullanılabiliyorsa tercih edilebilir.
- Yayın adresini Render size oluşturur (`https://…onrender.com`).

## Neler var?

- Bireysel ve takımlı canlı yarışma, anlık sıralama, dört renkli cevap şıkkı.
- Otomatik sayaç; tüm bağlı öğrenciler yanıt verince soru erken kapanır.
- Öğretmen soru bankası: soru ekleme / düzeltme / silme; CSV ve JSON dosyalarıyla içe/dışa aktarma.
- Hazır 6. sınıf çarpanlar, katlar ve asal sayılar soru havuzu.
- Mobil uyumlu arayüz, görsel efektler, QR kod ile öğrenci katılımı.
- CSV sonuç raporu.

## Teknik notlar

```text
app.py                   Python (aiohttp, WebSocket) canlı yarışma sunucusu
requirements.txt         Python bağımlılıkları
render.yaml              Render Blueprint için önerilen örnek
web/index.html           Öğretmen ve öğrenci canlı yarışma ekranları
web/klasik.html          Bireysel, çevrimdışı/tek oyunculu bölüm
web/sorular.json         Hazır sorular
OGRETMEN_KURULUM.md      Adım adım öğretmen yönergesi
```

Öğretmenin hazırladığı soru bankası tarayıcıda tutulur; **Dışa Aktar** ile yedek alın. Aktif odalar ve puanlar sunucu belleğinde tutulduğundan sunucu yeniden başlatılırsa sıfırlanır.

Bu proje eğitim amaçlıdır. Marka ve içerik paylaşımında kurumunuzun kullanım kurallarını gözetin.
