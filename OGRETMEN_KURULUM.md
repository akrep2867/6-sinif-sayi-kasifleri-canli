# SAYI KÂŞİFLERİ CANLI
## Öğretmenin kendi GitHub + Render hesabına BAĞIMSIZ kurulum kılavuzu

Bu klasörde oyunun **tüm kaynak dosyaları** bulunur. Kurulumdan sonra öğretmen kendi GitHub deposundan ve kendi Render hizmetinden yayın yapar; başka bir öğretmenin hesaplarına bağlanmaz. **Aynı Wi-Fi ağı gerekmez:** internet bağlantısı olan telefonlardan PIN/QR koduyla katılım mümkündür.

> **ÖNEMLİ:** Bu ZIP'i **GitHub'a ZIP olarak yüklemek yeterli değildir**. ZIP'i bilgisayarınızda açıp, içindeki dosyaları/klasörleri yeni GitHub deponuzun kök dizinine yükleyin.

### 1. GitHub hesabında yeni depo açın
1. https://github.com/new adresine gidin ve kendi GitHub hesabınızla oturum açın.
2. Depoya örneğin `sayi-kasifleri-matematik` adını verin. **Public** seçebilirsiniz; public olursa oyun kaynak kodları herkese görünür olur. Private repo seçimi de mümkündür, ancak Render erişim izni gerekir.
3. **Add README / .gitignore / License** kutularını boş bırakın; **Create repository** seçeneğine basın.
4. Bu paketi bilgisayarda **klasöre çıkartın**.
5. Yeni depoda **Add file > Upload files** yolunu açın. Paketin **oyun kaynak klasöründeki** şu dosyaları ve `web` klasörünü yükleyin:
   - `app.py`
   - `requirements.txt`
   - `render.yaml`
   - `web/index.html`
   - `web/klasik.html`
   - `web/sorular.json`
   - `README.md` ve `OGRETMEN_KURULUM.md` (isteğe bağlı, önerilir)
6. Dizin yapısının aynı kaldığını kontrol edin: `app.py` kökte; `index.html` **web klasörünün içinde** olmalıdır. **Commit changes** düğmesiyle kaydedin.

**Alternatif ve daha kolay yöntem:** https://github.com/new/import sayfasına gidin. Kaynak depo URL'sini kaynak olarak yazın; hedefi **kendi GitHub hesabınızda yeni bir depo** olarak seçin. Bu işlem depoya bağımsız bir **kopya** aktarır; sonrasında oyun sizin deponuzdadır. Kaynak bağlantısı: 
`https://github.com/akrep2867/6-sinif-sayi-kasifleri-canli` 
(Bu adres yalnızca **ilk kopyalama** için kullanılır, yayınlandıktan sonra oyun bu adresten çalışmaz.)

### 2. Render ile internette yayınlayın
1. https://dashboard.render.com adresinde **kendi** Render hesabınıza giriş yapın.
2. **New > Web Service** seçin. **Static Site seçmeyin.** Canlı yarışma Python sunucusu ve WebSocket kullanır.
3. GitHub'ı bağlayın. Listeden az önce **kendi hesabınızda** oluşturduğunuz `sayi-kasifleri-matematik` deposunu seçin.
4. Aşağıdaki yayın ayarlarını kullanın:

| Alan | Değer |
| --- | --- |
| Name | size ait benzersiz bir ad, örn. `sayi-kasifleri-6a` |
| Branch | `main` |
| Language / Runtime | `Python` |
| Root Directory | **boş** |
| Region | mümkünse Frankfurt |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python app.py` |
| Instance Type / Plan | **Free** (hesapta mevcutsa) |
| Auto-Deploy | **On** (tercih edilir) |

5. **Deploy Web Service** düğmesine basın. **Live** durumuna geçmesini bekleyin.
6. Render size `https://...onrender.com` biçiminde bir adres gösterecek. **Bu adres öğretmenin kendi adresidir; başka birinin adresi kullanılmaz.**
7. Adresi açarak öğretmen odası oluşturun; öğrencilerin telefonları QR/PIN ile katılabilsin.

### 3. Soru ekleme ve yarışmayı başlatma
1. Oyunda **Öğretmen: Canlı Oda > Canlı Yarışma Kur**.
2. **Soru Kaynağı** bölümünden **Hazır Sorular** veya **Kendi Sorularım** seçin.
3. Kendi sorularınızda soru metni, **A/B/C/D**, doğru yanıt ve açıklama ekleyin. İsterseniz CSV / JSON içe aktarın.
4. Süre, soru sayısı ve bireysel/takımlı ayarını seçip yarışmayı başlatın.
5. Bütün **aktif** öğrenciler cevap verdiyse süre beklenmeden soru kapanır.
6. Soruların doğru yanıtları soru kapanmadan öğrenci telefonuna gönderilmez.

### 4. Sorular, sonuçlar ve önemli uyarılar
- **Kendi Sorularım** bankası öğretmenin kullandığı tarayıcının yerel belleğinde (`localStorage`) saklanır. Başka cihazda görünmez. **Dışa Aktar** ile düzenli yedek alın.
- Tarayıcı verileri silinirse soru bankası kaybolabilir. Öğretmen başına en fazla **60 soru**, bir yarışmada en fazla **20 soru** kullanılabilir.
- Aktif oda, öğrenci listesi ve puanlar **sunucu belleğinde (RAM)** saklanır. Ücretsiz hizmet uyursa/yeniden başlarsa odalar sıfırlanabilir.
- Ücretsiz Render hizmeti kullanılmadığında uyuyabilir; ilk erişim biraz uzun sürebilir. Ücretlendirme ve Free planın güncel durumu Render hesabında kontrol edilmelidir.
- Öğrenci PIN'i **yalnızca ilgili öğretmenin Render adresinde** geçerlidir. Farklı öğretmenlerin odaları ve sonuçları birbirine karışmaz.
- Soru düzenleme / CSV yükleme **öğretmen cihazında** yapılmalıdır. Gerekirse öğrencilere vermek yerine kurumsal bilgisayar kullanın.
- Kodların paylaşımı yapılırsa marka, içerik ve kurum içi kullanım haklarına uygun davranılmalıdır.

### 5. Sık görülen sorunlar
- **404 / Not Found:** `app.py` kök dizinde ve `web/index.html` alt klasörde mi? **Static Site** değil **Web Service** oluşturuldu mu?
- **Build failed:** `requirements.txt` kökte mi; komut `pip install -r requirements.txt` olarak yazıldı mı?
- **Application failed:** Başlatma komutu tam olarak `python app.py` mi? Render > Logs bölümüne bakın.
- **QR kodla giriş açılmıyor:** QR öğretmenin yeni `onrender.com` adresi üzerinden mi oluşturuldu? `localhost` / yerel IP kullanmayın.
- **Eski ekran görünüyor:** Ctrl+F5 ile yenileyin.
- **Yarışma odası kayboldu:** Ücretsiz sunucu yeniden başlamış olabilir; yeni oda ve PIN oluşturun.
- **Öğrenciler birbirini görmüyor:** Herkesin aynı öğretmen linkini kullandığından emin olun.

**Proje düzeni**
```text
sayi-kasifleri-matematik/
├── app.py
├── requirements.txt
├── render.yaml
├── README.md
├── OGRETMEN_KURULUM.md
└── web/
    ├── index.html
    ├── klasik.html
    └── sorular.json
```
