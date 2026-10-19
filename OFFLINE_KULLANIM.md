# Sayı Kâşifleri — Okulda İnternetsiz Windows Sürümü

## Hangi durumda çalışır?

**Windows EXE**, oyun sunucusunu öğretmenin bilgisayarında çalıştırır ve tarayıcıda oyunu açar. Öğretmenin bilgisayarında, bu sürüm için internet erişimi gerekmez.

**Öğrencilerin telefonlarından katılması için telefon ve bilgisayarın birbirine ulaşabildiği aynı yerel ağda olması gerekir.** Bu ağ internetsiz bir Wi-Fi cihazı/erişim noktası veya öğretmenin telefonunun paylaştırdığı bir hotspot olabilir. Okul Wi-Fi'sinde cihazlar arası iletişim engelliyse katılım çalışmayabilir. Telefonların yalnızca kendi hücresel internetini kullanarak, tamamen internetsiz bir öğretmen bilgisayarına bağlanması mümkün değildir.

## EXE ile hızlı kullanım (Windows 10 / 11)

1. GitHub Actions'da oluşturulan **SayiKasifleri_Windows_Yerel_EXE.zip** dosyasını indirin ve klasöre çıkarın.
2. **SayiKasifleri_Yerel.exe** dosyasına çift tıklayın. Python kurulumu gerekmez. İmzalanmamış EXE için Windows güvenlik uyarısı görmeniz mümkündür; kurum güvenlik politikalarını izleyin.
3. Tarayıcınızda öğretmen sayfası açılır. Konsol penceresi açık kalmalıdır.
4. Sınıfın telefonlarını **bilgisayarla aynı Wi-Fi ağına/hotspot'a** bağlayın. Bağlantı internete çıkmak zorunda değildir. Büyük sınıflar için istemci izolasyonu kapalı, yeterli kapasitede bir erişim noktası kullanın.
5. Windows Güvenlik Duvarı sorarsa **özel ağ** için izin verin (kurumun izni gerekiyorsa okul BT ekibine danışın).
6. EXE'nin açtığı sayfada **Öğretmen > Canlı Yarışma Kur** ile odayı oluşturun. **QR kod** veya PIN sayesinde öğrenciler giriş yapar.
7. Öğrenciler telefonlarında `http://BILGISAYAR_IP:8765` adresini açar veya QR kodu okutur. EXE penceresinde kullanılabilir adresler yazar.
8. Yarışma bitince EXE konsolunu kapatın.

> Oyun localhost/127.0.0.1 adresinde açıldıysa bilgisayarda IP algılanamamıştır; internetsiz **yerel ağ bağlantısını** oluşturduktan sonra EXE'yi tekrar açın. QR kodunda localhost adresi öğrencide çalışmaz.

## Öğrenciler yalnızca kendi mobil verisini kullanmak istiyorsa?

Bu senaryoda okul bilgisayarının da **internet bağlantısı** olması ve herkesin aynı çevrimiçi oyuna katılması gerekir. Okul ağı mevcut siteyi engelliyorsa, okul politikalarına uygun şekilde bilgisayara öğretmen telefonundan USB internet paylaşımı sağlamak veya okul BT'den gerekli erişimi istemek bir seçenektir.

Öğretmenin internetten katıldığı durumda mevcut online sürüm kullanılabilir:
https://six-sinif-sayi-kasifleri-canli.onrender.com

**Bilgisayar tamamen internetsiz + öğrenciler farklı operatör ağlarında = canlı senkronizasyon mümkün değil.** EXE tek başına bunu değiştirmez.

## Öğretmen soruları ve veri saklama

- Öğretmen soru bankası tarayıcının yerel saklama alanındadır. Dışa aktar/yedekle özelliğini kullanın.
- Sunucu EXE kapatıldığında öğrenci oturumları, puanlar ve aktif yarışma sona erer.
- Bilgisayardaki yerel web sunucusu başka bir servise, senin Render/GitHub hesabına veya internete bağlanmaz.
- Sınıfta açılan bu yerel URL, `http://` ile çalışır; güvenilir özel ağlarda kullanın. Genel internete veya okul dışına açmayın.
- Ağ istemci izolasyonu, Windows güvenlik duvarı veya antivirüs engeli varsa okulun BT yöneticisiyle çalışın.
- Büyük sınıflarda telefon hotspot cihazlarının istemci sınırları olabilir; uygun yerel kablosuz erişim noktası gerekir.

## Kaynaktan geliştirme (teknik kullanım)

```powershell
py -m pip install -r requirements.txt
py offline_launcher.py
```

EXE, GitHub Actions'ın `windows-latest` Windows ortamında PyInstaller kullanarak üretilir. Kod ve varsa sonraki güncellemeler için bu deponun **Actions > Windows Offline EXE** iş akışına bakın.
