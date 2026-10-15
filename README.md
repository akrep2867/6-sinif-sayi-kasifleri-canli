# SAYI KÂŞİFLERİ CANLI — İNTERNETTEN OYNANAN 6. SINIF MATEMATİK YARIŞMASI

Çarpanlar, katlar, asal sayılar. **Aynı Wi-Fi ağı gerekmiyor**: öğrenciler kendi mobil internetleriyle aynı HTTPS adresinden veya QR koddan katılır.

## 🌍 İnternette açmak için tek düğme

[![Render’a yayımla](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/akrep2867/matematik-macerasi-doga-koleji/tree/sayi-kasifleri-canli)

1. Yukarıdaki düğmeye tıkla. Render hesabınla giriş yap ve gerekirse GitHub hesabına erişim izni ver. Bu özel GitHub deposunu Render'a bağla.
2. Açılan ekranda **Free** planı seçip **Apply / Deploy** işlemini onayla. Render internet adresini (örneğin `https://sayi-kasifleri-canli.onrender.com`) oluşturur.
3. Bu adresi bilgisayarda/akıllı tahtada aç: **Canlı Yarışma Kur** → odayı aç → öğrenciler **herhangi bir ağ üzerinden** QR kodu okutsun veya linke dokunsun.

**Henüz Render'da yayımlanmadıysa bir genel oyun adresi yoktur.** Bu buton hesabında yeni bir sunucu açmanı başlatır, otomatik olarak hesap açmaz.

## ⚡ Sınıfta kullanma

- Öğretmen: aynı siteden yarışma oluşturur, 6 haneli PIN ve QR gösterir, yarışmayı başlatır.
- Öğrenciler: kendi mobil verisinden girer; ayrı uygulama kurmaz, yalnızca bir rumuz yazar.
- Bireysel veya 2–4 takımla yarışma, hız puanı, süre, canlı sıralama ve CSV sonucunu indirme vardır.
- 56 soruluk havuz: çarpanlar, katlar, asal sayılar.
- Önceki cihaz-üstü bireysel oyun ve Sınıf Arenası **`/klasik`** yolunda durur.

## Dikkat

- Ücretsiz Render web servisi 15 dakika işlemsiz kaldığında uykuya geçebilir, tekrar açılması yaklaşık bir dakika sürebilir. Sınıfa girmeden önce siteyi açarak çalıştığını kontrol et.
- Sunucu yeniden başlarsa, RAM'de tutulan aktif yarışmalar ve puanlar sıfırlanır. Yalnızca tek sunucu örneği çalıştır.
- Öğrencilere soyadları yerine rumuz kullanmalarını söyle; sonuç CSV'sini kendin sakla.
- Ücretsiz plan ders içindeki deneme için uygundur; düzenli ve kritik kullanım için daha güvenilir ücretli barındırma değerlendir.

## Teknoloji

Python `aiohttp` + WebSocket, HTML5/JavaScript. Sunucu oyun PIN'ini, cevap sürelerini ve puanları kontrol eder. `render.yaml` hazırdır. Canlı bağlantı `wss://` üzerinden kullanılır.