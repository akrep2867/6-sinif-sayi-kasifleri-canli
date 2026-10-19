"""Sayı Kâşifleri CANLI — bağımsız Windows / yerel ağ başlatıcısı.

Oyun sunucusu tamamen bilgisayar üzerinde çalışır. İnternet gerektirmez;
öğrenci telefonlarının oyuna ulaşabilmesi için aynı yerel Wi-Fi/hotspot gerekir.
"""
import ipaddress
import socket
import sys
import threading
import time
import webbrowser

from aiohttp import web
import app as game


def local_addresses():
    """Kullanılabilir yerel IPv4 adreslerini dış ağa veri göndermeden bul."""
    addresses = []
    def add(ip):
        try:
            addr = ipaddress.ip_address(ip)
            if addr.version == 4 and addr.is_private and not addr.is_loopback and not addr.is_link_local:
                if ip not in addresses:
                    addresses.append(ip)
        except ValueError:
            pass
    for target in (("192.0.2.1", 80), ("10.255.255.1", 80)):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect(target)
            add(sock.getsockname()[0])
        except OSError:
            pass
        finally:
            sock.close()
    try:
        for entry in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET, socket.SOCK_STREAM):
            add(entry[4][0])
    except OSError:
        pass
    return sorted(addresses, key=lambda ip: (not ip.startswith("192.168."), not ip.startswith("172."), ip))


def browser_open(url):
    time.sleep(1.6)
    try:
        webbrowser.open(url, new=2)
    except Exception:
        pass


def main():
    port = 8765
    ips = local_addresses()
    teacher_url = "http://" + (ips[0] if ips else "127.0.0.1") + ":" + str(port)
    line = "=" * 64
    print("\n" + line)
    print("      SAYI KASIFLERI CANLI - INTERNET GEREKTIRMEZ")
    print(line)
    print("OGRETMEN EKRANI : " + teacher_url)
    if ips:
        print("\nOGRANCI TELEFONUNDAN OYUNA KATILMA:")
        for ip in ips:
            print("    http://" + ip + ":" + str(port))
        print("\nTelefonlar ve bilgisayar AYNI yerel Wi-Fi/hotspot aginda olmalidir.")
        print("Kendi MOBIL INTERNETI ile baska agdan baglanmak mumkun DEGILDIR.")
    else:
        print("\nBilgisayarda yerel ag bulunamadi.")
        print("Oyun bilgisayarda acilir ama ogrenciler baglanamaz.")
        print("Yerel bir Wi-Fi / erisim noktasina baglanip EXE'yi yeniden acin.")
    print("\nWindows guvenlik duvari sorarsa OZEL AGLAR icin izin verin.")
    print("Bu pencere acik kaldigi surece oyun calisir. Kapatmak icin Ctrl+C.")
    print(line + "\n", flush=True)
    threading.Thread(target=browser_open, args=(teacher_url,), daemon=True).start()
    try:
        web.run_app(game.app, host="0.0.0.0", port=port, access_log=None, print=None)
    except OSError as err:
        print("\nPort 8765 acilamadi: " + str(err))
        print("Bu programin ikinci kopyasi acik olabilir. Digerini kapatin.")
        input("Kapatmak icin ENTER tusuna basin...")
        return 1
    except KeyboardInterrupt:
        print("\nYarisma kapatildi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
