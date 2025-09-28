Teknik Yığın - ESN PULSE
Versiyon: 1.0.0 - 28.09.2025
Genel Bakış
ESN PULSE, etkinlik verilerini scrape edip yerel PostgreSQL veritabanına kaydeden bir araçtır. MVP, local makinede çalışır ve manuel tetiklenir.
Teknik Yığın

Dil: Python 3.12
Web Scraping:
aiohttp: Asenkron HTTP istekleri.
BeautifulSoup4: HTML ayrıştırma.
Pydantic: Veri validasyonu.


Veritabanı:
PostgreSQL: Local, normalize veri saklama + metadata tracking.
asyncpg: Asenkron DB işlemleri.
Metadata Tracking: sections.last_scraped ile akıllı öncelik sistemi.


CLI:
argparse: Manuel tetikleme komutları.


Loglama:
logging: Hata ve başarı logları (logs/scrape.log).


Konteynerleştirme:
Docker Compose: Local kurulum.


Bağımlılık Yönetimi:
python-dotenv: Çevresel değişkenler (.env).



Bağımlılıklar
requirements.txt:
aiohttp==3.9.5
beautifulsoup4==4.12.3
pydantic==2.8.2
asyncpg==0.29.0
python-dotenv==1.0.1

Kurulum Notları

Postgres: Local, port 5434, .env'de DB_URL.
Loglar: logs/ klasöründe saklanır.
Docker Compose: Opsiyonel, DB ve scraper için.
