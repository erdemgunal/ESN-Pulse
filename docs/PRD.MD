# Ürün Gereksinim Dokümanı (PRD) - ESN PULSE

Versiyon: v1.0.2 - 01.08.2025

## 1. Giriş

Bu doküman, ESN PULSE projesini detaylandırmaktadır. Proje, ESN (Erasmus Student Network) ağındaki 46 ülkenin tamamında ve bu ülkelere bağlı 517 şubenin çeşitli platformlarından (`accounts.esn.org` ve `activities.esn.org`) otomatik olarak veri çekecek, depolayacak ve analiz için hazır hale getirecek bir veri scraper projesidir. ESN PULSE’un temel amacı, ESN şubelerinin operasyonel ve istatistiksel verilerini merkezi bir veritabanında toplayarak, daha bilinçli kararlar alınmasına, şubeler arası karşılaştırmaların yapılmasına ve genel performansın uluslararası düzeyde izlenmesine olanak sağlamaktır.

Stakeholder Bağlamı: ESN PULSE, başlangıçta ESN Marmara şubesi için yerel bir analiz aracı olarak geliştirilecek ve kendi bilgisayarımda çalışacaktır. Daha sonra, diğer ESN şubelerine veri erişimi sağlamak için bir web arayüzü oluşturulacak ve potansiyel olarak ESN Türkiye web komitesine entegre edilecektir. Proje, ESN International’ın şube performansını izleme ve etkinlik planlamasını iyileştirme hedefleriyle uyumludur.

-----

## 2. Amaç ve Hedefler

### 2.1. Temel Amaç

ESN ağındaki tüm şubelerin (46 ülke, 517 şube) faaliyetlerini ve performanslarını gösteren çevrimiçi kaynaklardan düzenli ve otomatik olarak veri toplayarak, bu verileri yapılandırılmış bir veritabanında depolamak ve anlamlı içgörüler elde etmek için küresel bir temel oluşturmaktır.

### 2.2. Hedefler (Öncelik Sırasına Göre)

  * Veri Bütünlüğü ve Kalitesi: `accounts.esn.org` ve `activities.esn.org` platformlarından tüm 46 ülke ve 517 şubeye ait temel bilgiler, etkinlik detayları ve istatistiksel verilerin eksiksiz, doğru, valide edilmiş ve temizlenmiş bir şekilde toplanması.
  * Otomasyon: Veri toplama sürecinin manuel müdahale gerektirmeden düzenli (aylık veya haftalık) çalışması.
  * Ölçeklenebilirlik: Gelecekte daha fazla şube, platform veya veri hacmi eklendiğinde sistemin performansını koruyabilmesi. Mevcut 517 şubeden gelen veri yoğunluğunu kaldırabilecek bir mimari.
  * Analiz Desteği: Toplanan verilerin Power BI, Tableau gibi iş zekası araçlarıyla veya özel Python betikleriyle entegre edilerek anlamlı raporlar ve görselleştirmeler oluşturulması. Raporlar, uluslararası düzeyde trendleri ve şube performanslarını karşılaştırmaya olanak tanıyacak.
  * Kullanıcı Dostu Erişim: Teknik olmayan ESN gönüllülerinin verilere basit SQL veya BI araçlarıyla 1 saatlik eğitimle erişebilmesi.
  * Güvenilirlik: Ağ hataları, timeout’lar veya sunucu sorunları gibi durumlarda scraping sürecinin dayanıklı olması ve hataları yönetmesi.

### 2.3. Uyumluluk ve Etik

  * Tüm veriler, `accounts.esn.org` ve `activities.esn.org` platformlarından yalnızca halka açık bilgiler alınarak toplanacaktır. ESN International’dan scraping izni alınacak ve belgelenerek platformların kullanım koşullarına uyum sağlanacaktır.
  * GDPR uyumluluğu: Kişisel veriler (örn. katılımcı isimleri, e-postalar) toplanmayacak veya anonimleştirilecektir.
  * ESN International ile iletişime geçilerek veri toplama izni doğrulanacaktır (örneğin, e-posta ile onay alınacak).

-----

## 3. Kapsam (In-Scope)

### 3.1. Veri Kaynakları

  * `accounts.esn.org`: Tüm 46 ülkenin ve 517 şubenin temel bilgileri, iletişim detayları, sosyal medya linkleri.
  * `activities.esn.org`: ESN şubelerinin düzenlediği etkinliklerin listeleri (geçmiş ve gelecek), etkinlik detayları (tarih, yer, amaç, nedenler, SDGs, hedefler, katılımcılar), şube bazında istatistiksel veriler (toplam etkinlik sayısı, katılımcı dağılımları, neden ve tür bazlı istatistikler).

### 3.2. Çekilecek Veri Kategorileri

#### 3.2.1. Ülke Bilgileri (`countries` tablosu)

  * Ülke adı, ülke kodu, slug, URL, şube sayısı.

#### 3.2.2. Şube Bilgileri (`sections` tablosu)

  * `id`: SERIAL PRIMARY KEY (Şubenin benzersiz tanımlayıcısı, `activity_section_organisers` gibi ilişki tablolarında foreign key olarak kullanılır).
  * Şube Adı: (Örn. "ESN METU", `accounts.esn.org/country/<country_code>` sayfasındaki şube listesinden çekilir.)
  * Bağlı olduğu ülke: (Örn. "Türkiye")
  * Slug'lar:
    * `accounts_platform_slug`: VARCHAR(255) (Örn. "tr-anka-met")
    * `activities_platform_slug`: VARCHAR(255) (`Şube Adı` kullanılarak oluşturulan ve `activities.esn.org`'da doğrulanmış slug. Örn. "esn-metu")
  * URL'ler:
    * `accounts_url`: (Örn. https://accounts.esn.org/section/tr-anka-met)
    * `activities_url`: (Örn. https://activities.esn.org/organisation/esn-metu)
  * Logo URL’si: (Örn. /`sites/default/files/styles/medium/public/organisation-logos/esn/TR-ANKA-MET.png.webp?itok=DnD8WNMR`)
  * Şehir: (Örn. "Ankara")
  * Adres: (Örn. "Üniversiteler Mahallesi...")
  * İletişim bilgileri:
    * e-posta: (Örn. `esnmetu@metu.edu.tr`)
    * web sitesi: (Örn. `https://metu.esnturkey.org/`)
    * sosyal medya: (JSONB, örn. `{"facebook": "...", "instagram": "..."}`)
  * `university_name`: VARCHAR(255) (Örn. "Middle East Technical University")
  * Coğrafi koordinatlar:
    * `longitude`: DECIMAL(9,6)
    * `latitude`: DECIMAL(9,6)
  * `country_code`: VARCHAR(10) FOREIGN KEY (Ülke Kodu).
  * `can_scrape_activities`: BOOLEAN (Şubenin `activities.esn.org` verilerinin çekilip çekilemeyeceğini gösteren bayrak).
  * `last_validated_activities_slug`: TIMESTAMP (Son `activities_platform_slug` doğrulama zaman damgası).
  * `last_scraped`: TIMESTAMP (Şubenin etkinlik ve istatistik verilerinin son scrape edildiği zaman damgası, `NULL` ise hiç scrape edilmemiştir).

#### 3.2.3. Etkinlik Bilgileri (`activities` tablosu)

Alanlar:
  * `title`: VARCHAR(255) (etkinlik adı, örn. "Boat Party").
  * `event_participantsslug`: VARCHAR(255) (benzersiz etkinlik tanımlayıcısı, örn. "boat-party-20885").
  * `url`: VARCHAR(255) (etkinlik sayfası URL’si, örn. https://activities.esn.org/activity/boat-party-20885).
  * `description`: TEXT (etkinlik açıklaması, örn. "ESNers were entertained with a variety of content and had a look at the Bosphorus in the evening.").
  * `start_date`: DATE (etkinlik başlangıç tarihi, ISO formatında, örn. "2023-11-08").
  * `end_date`: DATE (etkinlik bitiş tarihi, ISO formatında).
  * `city`: VARCHAR(100) (etkinlik şehri, örn. "Istanbul").
  * `country_code`: VARCHAR(10) (ülke kodu, örn. "TR", `countries` tablosuna foreign key bağlantısı ile veri tutarlılığı sağlanır).
  * `participants`: INTEGER (toplam katılımcı sayısı, örn. 160, negatif olamaz).
  * `activity_type`: VARCHAR(100) (etkinlik türü, örn. "Game or Social Activity").
  * `is_future_event`: BOOLEAN (etkinlik gelecekte mi, geçmişte mi; true/false).
  * `is_valid`: BOOLEAN (etkinlik verisinin geçerliliği, varsayılan true).

**Veri Tutarlılığı:**
  * `activities.country_code` alanı `countries.country_code` tablosuna `FOREIGN KEY` constraint ile bağlanır
  * `ON UPDATE CASCADE` ile country_code güncellemeleri otomatik yayılır
  * `ON DELETE SET NULL` ile ülke silindiğinde activity kayıtları korunur

İlişki Tabloları (Many-to-Many İlişkiler İçin):
  * `activity_section_organisers` tablosu: (`activity_id`, `section_id`)
      * Bu tablo, bir etkinliğin birden fazla şube tarafından düzenlenebildiği senaryoyu yönetir.
  * `activity_to_cause` tablosu: (`activity_id`, `cause_id`)
      * `activity_causes` tablosundaki nedenleri (örn. "Culture", "Education & Youth") etkinliklerle ilişkilendirir.
  * `activity_to_sdg` tablosu: (`activity_id`, `sdg_id`)
      * `sdgs` tablosundaki Sürdürülebilir Kalkınma Hedeflerini (örn. "SDG 3") etkinliklerle ilişkilendirir.
  * `activity_to_objective` tablosu: (`activity_id`, `objective_id`)
      * `objectives` tablosundaki detaylı hedefleri (örn. "Mental Health & Well-Being") etkinliklerle ilişkilendirir.

Validasyon:
  * Zorunlu alanlar: `title`, `event_slug`, `url`, `description` (boş olamaz).
  * Formatlar: `start_date` ve `end_date` ISO formatında (YYYY-MM-DD), `participants` negatif olamaz, diğer liste tabanlı alanlar (`organisers`, `sdgs`, `objectives`, `causes`) geçerli metin listeleri içermeli, `activity_type` geçerli metin olmalı.
  * Geçersiz veriler `validation_errors` tablosuna kaydedilir.

Kenar Durumlar:

  * Eksik veya hatalı alanlar (örn. geçersiz tarih, negatif katılımcı, boş açıklama) `validation_errors` tablosuna loglanır.
  * Eksik veya hatalı veri içeren etkinlikler `is_valid=False` işaretlenir.

#### 3.2.4. Şube İstatistikleri (`section_overall_statistics`, `section_cause_statistics`, `section_type_statistics`, `section_participant_statistics` tabloları)

Veri Kaynağı: activities.esn.org/organisation/<slug>/statistics adresinden çekilen JSON verisi.
  
  * Fiziksel ve Çevrimiçi Etkinlik Sayıları: `total_activities`
    * `physical_activities`: `activities_statistics.total_activities.values[0][1]`
    * `online_activities`: `activities_statistics.total_activities.values[1][1]`
  * Katılımcı Sayıları: `total_participants`
    * `total_local_students`: `activities_statistics.total_participants.values[0][1]`
    * `total_international_students`: `activities_statistics.total_participants.values[1][1]`
    * `total_coordinators`: `activities_statistics.total_participants.values[2][1]`
  * Nedenlere Göre Etkinlikler: `section_cause_statistics`
    * `total_causes`: `activities_statistics.total_causes.values`
    * `physical_causes`: `activities_statistics.physical_causes.values`
    * `online_causes`: `activities_statistics.online_causes.values`
  * Türlere Göre Etkinlikler: `section_type_statistics`
    * `physical_types`: `activities_statistics.physical_types.values`
    * `online_types`: `activities_statistics.online_types.values`
  * Katılımcı Türlerine Göre Etkinlikler: `section_participant_statistics`
    * `physical_participants`: `activities_statistics.physical_participants.values`
    * `online_participants`: `activities_statistics.online_participants.values`

**Performans Optimizasyonları:**
  * İstatistik tablolarında `section_id` alanları üzerine indexler performansı %300-500 artırır
  * `(section_id, category_name)` composite indexleri analitik sorgular için optimize edilmiştir
  * `UNIQUE` constraints ile veri tekrarı önlenir (örn. `section_id + cause_name` kombinasyonu)
  * BI araçları (Power BI, Tableau) için hızlı veri erişimi sağlanır

### 3.3. Veri Tazeliği

  * AccountsScraper: Aylık veya manuel tetiklemeyle.
  * ActivitiesAndStatisticsScraper: Haftalık olarak, platformdaki güncellemelerden sonra maksimum 7 gün gecikme.

### 3.4. Kapsam Dışı (Out-of-Scope)

  * Gerçek zamanlı veri toplama (yalnızca aylık/haftalık toplu işleme).
  * ESN dışındaki veri kaynakları (örn. sosyal medya API’leri).
  * Web arayüzü veya AI destekli etkinlik planlayıcı (Faz 2 ve Faz 3’te ele alınacak).
  * Çok dilli veri işleme (başlangıçta yalnızca İngilizce veri saklanacak).

### 3.5. Kenar Durumlar

  * Eksik Veri: `activities_platform_slug` olmayan şubeler `can_scrape_activities`=False olarak işaretlenir.
  * Hatalı Veri: Geçersiz veriler `validation_errors` tablosuna loglanır.
  * Eksik İstatistikler: İstatistik sayfası JSON verisi döndürmeyen şubeler için ilgili tablolara sıfırlanmış varsayılan kayıtlar eklenir.

-----

## 4. Teknik Mimari

### 4.1. Genel Bakış

ESN PULSE, başlangıçta yerel bir makinede çalışacak, Python tabanlı bir scraping motoru, Celery görev kuyruğu ve PostgreSQL veritabanından oluşacaktır. Yerel geliştirme ve test için Docker Compose kullanılacak, gelecekte web tabanlı dağıtım için Kubernetes veya bulut tabanlı bir çözüm (örn. Heroku, AWS) değerlendirilecektir. Mimari, 517 şubeden gelen veri yoğunluğunu kaldırabilecek şekilde tasarlanmıştır.

### 4.2. Bileşenler

#### 4.2.1. Web Scraper Modülü (Python)

Kütüphaneler:

  * Kütüphaneler: `aiohttp`, `asyncio`, `BeautifulSoup4/lxml`, `json`, `asyncpg`, `Celery`, `python-slugify`, `Pydantic`.

Modüller:
  * AccountsScraper: `accounts.esn.org`’dan ülke ve şube bilgilerini çeker, `countries` ve `sections` tablolarına yazar.
  * ActivitiesAndStatisticsScraper: `activities.esn.org`’dan etkinlik ve istatistik verilerini çeker, `activities`, `activity_causes`, ve istatistik tablolarına yazar.

Fonksiyonellik:

  * Asenkron HTTP istekleri.
  * HTML ve JSON ayrıştırma.
  * Veri validasyonu (Pydantic modelleri ile).
  * `activities_platform_slug` Validasyonu: HTTP HEAD isteği (200 OK) ile URL geçerliliği kontrol edilir.
  * Hata yönetimi: HTTP hataları için 3 yeniden deneme, üstel geri çekilme (exponential backoff).
  * Basit Rate Limiting: Platformlara yük bindirmemek için sabit 0.5 saniye gecikme.
  * User-Agent Rotasyonu: Güvenilirlik için farklı User-Agent’lar kullanma.
  * Hatalı veriler `validation_errors` tablosuna, başarısız istekler `failed_scrapes` tablosuna kaydedilir.

#### 4.2.2. Veritabanı (PostgreSQL)

Rol: Çekilen verilerin yapılandırılmış depolanması.
Şema: `countries`, `sections`, `activities`, `activity_causes`, `sdgs`, `objectives`, `activity_section_organisers`, `activity_to_cause`, `activity_to_sdg`, `activity_to_objective`, `section_overall_statistics`, `section_cause_statistics`, `section_type_statistics`, `section_participant_statistics`, `validation_errors`, `failed_scrapes`, `scraper_status` tabloları.

Özellikler:

  * **Veri Tutarlılığı:** Foreign key constraints (`activities.country_code` → `countries.country_code`) ile referansiyel bütünlük
  * **Benzersiz Kısıtlamalar:** `sections` için `slug`, `activities` için `event_slug`, istatistik tablolarında `(section_id, category_name)` kombinasyonları
  * **Performans İndexleri:** 
    - Temel alanlar: `section_id`, `country_code`, `start_date`, `is_valid`
    - Composite indexler: `(section_id, cause_name)`, `(section_id, activity_type)`, `(section_id, participant_type)`
    - Partial indexler: Sadece aktif kayıtlar (`WHERE is_valid = TRUE`, `WHERE can_scrape_activities = TRUE`)
  * **Yedekleme:** Haftalık `pg_dump` yedeklemesi
  * **Gelecek:** Bağlantı havuzlama için PgBouncer ve okuma replikaları

#### 4.2.3. Görev Kuyruğu (Celery)

  * Broker: Redis.
  * Worker'lar: Başlangıçta tek worker.
  * Fonksiyonellik: Görev bağımlılıklarını (`chain` fonksiyonu ile), asenkron ve paralel işlemeyi yönetir.

#### 4.2.4. Konteynerleştirme (Docker)

  * PostgreSQL, Celery ve scraper, Docker Compose ile paketlenecektir.

#### 4.2.5. Test Stratejisi

  * Birim Testleri: `pytest` ile ayrıştırma mantığı test edilir (örn. şube adı, etkinlik detayları çıkarma, %80 kapsama). Veri validasyon kuralları test edilir.
  * Entegrasyon Testleri: Sahte HTML/JSON verileriyle uçtan uca test (10 şube için). Scraper modülleri arasındaki veri akışı test edilir.
  * Manuel Doğrulama: Her ay, eksik/geçersiz kayıtlar için SQL sorguları (örn. `SELECT * FROM activities WHERE is_valid = False` veya `SELECT * FROM validation_errors`).


-----

## 5. Veri Akışı ve İşlemler

Ana Orkestrasyon Scripti (`run_scraper.py`):

  * `run_scraper.py` adında bir ana orkestrasyon scripti, `scraper_status` tablosunu ve `sections` tablosunu kontrol ederek scraping akışını yönetir.
  * İlk Çalıştırma / Bağımlılık Yönetimi: Eğer `sections` tablosu boşsa veya `AccountsScraper`’ın son başarılı çalışması 30 günden eskiyse, `AccountsScraper` Celery görevi otomatik olarak tetiklenir ve tamamlanana kadar `ActivitiesAndStatisticsScraper` bekletilir. Bu sıralı bağımlılık, Celery’nin `chain` fonksiyonu ile yönetilir (`accounts_scraper_task.s() | activities_scraper_task.s()`).

### 5.1. AccountsScraper İş Akışı (Aylık veya İsteğe Bağlı)

  * `https://accounts.esn.org/` adresinden tüm ülkeler ve ilgili URL'leri çekilir.
  * Her ülke için, `https://accounts.esn.org/country/<country_code>` sayfası ziyaret edilir.
  * Bu sayfadaki şube listesi (`<span class="field-content">`) içinden şubelerin adları ve `accounts_platform_slug`'ları (`href`'lerden) çekilir.
  * Çekilen bu şube listesi, veritabanındaki sections tablosu ile karşılaştırılır. Veri tabanında olmayan veya `can_scrape_activities` bayrağı `NULL` olan (yani doğrulama işlemi tamamlanmamış) şubeler öncelikli olarak işlenir.
  * Çekilen şube adından ("ESN METU") bir slug ("esn-metu") oluşturulur. Bu, `activities_platform_slug` olarak atanır.
  * Oluşturulan `activities_platform_slug`'un geçerliliği `https://activities.esn.org/organisation/<slug>/activities` adresine bir HTTP HEAD isteği gönderilerek kontrol edilir.
  * Geçerli olan şubeler için `can_scrape_activities` bayrağı `True` olarak ayarlanır.
  * Veriler `sections` tablosuna UPSERT edilir.

### 5.2. ActivitiesAndStatisticsScraper İş Akışı (Haftalık)

  * Veri tabanındaki `sections` tablosundan `can_scrape_activities=True` olan şubeler çekilir ve `last_scraped` alanına göre sıralanır (ORDER BY last_scraped ASC NULLS FIRST). Bu, hiç scrape edilmemiş (`last_scraped IS NULL`) veya en eski scrape edilmiş şubelerin önceliklendirilmesini sağlar.
  * Her şube için, etkinlik listesi sayfası (a`ctivities.esn.org/organisation/<slug>/activities`) ziyaret edilir.
  * Paginasyon: "Last" bağlantısı kullanılarak tüm sayfalar belirlenir ve paralel olarak çekilir.
  * Her sayfadan etkinlik özetleri alınır ve her bir etkinlik için detay sayfası (`activities.esn.org/activity/<event_slug>`) çekilir.
  * Etkinlik detaylarından tüm alanlar (başlık, açıklama, katılımcı sayısı, SDG'ler, nedenler) çekilerek `activities` ve ilgili ilişki tablolarına UPSERT edilir.
  * Aynı şube için istatistik sayfası (`activities.esn.org/organisation/<slug>/statistics`) çekilir ve doğrudan JSON verisi ayrıştırılarak istatistik tablolarına UPSERT edilir.
  * Başarılı scrape sonrası, `sections` tablosundaki `last_scraped` alanı güncellenir.
  * Başarısız istekler `failed_scrapes` tablosuna loglanır.

#### 5.2.1. Etkinlik Listeleri ve Detayları (`activities.esn.org`/organisation/<slug>/activities)

  * İlgili şubenin `activities.esn.org/organisation/<slug>/activities` sayfasını ziyaret eder.
  * Paginasyon Yönetimi:
      * İlk sayfa (`?page=0`) çekilir ve `<nav>` etiketindeki "Last" bağlantısı (örn. `<a href="?page=27">`) ayrıştırılarak toplam sayfa sayısı belirlenir (`BeautifulSoup` ile).
      * Sayfalar, 5’li gruplar halinde parçalara (chunk) bölünür (örn. 27 sayfa için: [0-4], [5-9], [10-14], [15-19], [20-24], [25-27]).
      * Her parça, bir Celery görevine atanır ve sayfalar asenkron olarak (`aiohttp` ile, 0.5 saniye gecikme) paralel şekilde çekilir.
  * Her sayfadaki etkinlikler (`<article class="node ct-physical-activity ct-physical-activity--full">`) ayrıştırılır:
      * `title` (`.field__item h1` veya `.activity-label`’den).
      * `event_slug` (`.url`’den, örn. "boat-party-20885").
      * `url` (`.url`’den, örn. "`https://activities.esn.org/activity/boat-party-20885`").
      * `description` (`.ct-physical-activity__field-ct-act-description .field__item`’den).
      * `start_date`, `end_date` (`.highlight-dates-single span`’den, ISO formatına çevrilir).
      * `city`, `country_code` (`.highlight-data-text span`’den).
      * `organisers` (`.pseudo__organisers .pseudo__organiser a`’dan, liste olarak, `activity_section_organisers` tablosuna `section_id` ile bağlanır).
      * `participants` (`.highlight-data-number .highlight-data-text-big`’den, tamsayıya çevrilir).
      * `sdgs` (`.field-sdgs-wrapper img`’lerin alt özniteliklerinden, örn. "SDG 3").
      * `objectives` (`.activity__objectives .field__item span`’den).
      * `causes` (`.activity-causes .activity-label a`’dan).
      * `activity_type` (`.activity-types .activity-type a`’dan).
      * `is_future_event` (tarihe göre belirlenir, gelecekteyse `true`).
  * Veriler Pydantic ile valide edilir (örn. boş olmayan `description`, negatif olmayan `participants`).
  * Valide edilen veriler `activities` ve ilgili ilişki tablolarına (`activity_section_organisers`, `activity_to_cause`, `activity_to_sdg`, `activity_to_objective`) UPSERT edilir.
  * Başarılı scrape sonrası, ilgili şubenin `last_scraped` alanı güncellenir (`UPDATE sections SET last_scraped = NOW() WHERE shube_slug = '<slug>'`).
  * Başarısız sayfalar (örn. timeout, 404) `failed_scrapes` tablosuna kaydedilir ve 3 kez yeniden denenir (üstel geri çekilme ile).

#### 5.2.2. Şube İstatistikleri (`activities.esn.org`/organisation/<slug>/statistics)

  * Celery, her şube için istatistikleri çeker ve JSON verisini ayrıştırır.
  * JSON verisi ayrıştırılır ve ilgili istatistik tablolarına UPSERT edilir.
  * Başarılı istatistik scrape’i sonrası da `last_scraped` güncellenir.

### 5.3. Veritabanı Kaydı ve Hata Yönetimi

  * Veritabanı Kaydı: Tüm çekilen, işlenen ve valide edilen veriler, belirlenen veritabanı şemasına uygun olarak PostgreSQL’e kaydedilir. Geçersiz veriler `validation_errors` tablosuna kaydedilir.
  * Hata Yönetimi: Başarısız istekler `failed_scrapes` tablosuna kaydedilir ve 3 kez yeniden denenir (üstel geri çekilme). Zaman aşımı sınırları (örn. `AccountsScraper` için 1 saat, `ActivitiesAndStatisticsScraper` için 2 saat) uygulanarak uzun süreli kesintiler önlenir. Kısmi başarı durumunda sadece `can_scrape_activities=True` olan şubeler için etkinlik scraping’i devam eder.
  * Tekilleştirme: Benzersiz kısıtlamalar (`sections(slug)`, `activities(event_slug)`) kullanılarak veri tekrarı önlenir.

### 5.4. Manuel Tetikleme Mekanizması

  * Komut Satırı: `run_scraper.py` scripti, `argparse` ile komut satırı seçenekleri sunar:
      * `python run_scraper.py --module accounts`: `AccountsScraper`’ı tetikler.
      * `python run_scraper.py --module activities`: `ActivitiesAndStatisticsScraper`’ı tüm geçerli şubeler için tetikler.
      * `python run_scraper.py --module activities --section esn-yildiz`: Sadece belirli bir şube için `ActivitiesAndStatisticsScraper`’ı tetikler.
      * `python run_scraper.py --module all`: Tüm scraper modüllerini (`AccountsScraper` sonra `ActivitiesAndStatisticsScraper`) bağımlılıkları gözeterek çalıştırır.
  * `ActivitiesAndStatisticsScraper`, tetiklendiğinde `sections` tablosunda geçerli veri olup olmadığını kontrol eder.
  * API (Faz 2 İçin): FastAPI ile HTTP uç noktaları (`/trigger_scraper?module=activities&section=esn-yildiz`) eklenerek uzaktan tetikleme sağlanır. API anahtarıyla güvenlik korunur.
  * Hatalı şube slug’ları loglanır, aynı anda çalışan görevler için Redis tabanlı kilitler kullanılır ve tüm tetiklemeler `logs/scrape_YYYY-MM-DD.log` dosyasına kaydedilir.

-----

## 6. Ölçeklenebilirlik, Dayanıklılık ve İzleme

### 6.1. Ölçeklenebilirlik

  * Yatay Ölçekleme (Celery Workers): Celery worker’ları, yüksek performans ve paralel işleme için kolayca ölçeklendirilebilir. Mevcut 517 şube ve artan veri hacmi göz önüne alındığında bu hayati önem taşımaktadır.
  * Asenkron İşleme (Asyncio & Aiohttp): Python’da I/O yoğun görevlerde (HTTP istekleri, veritabanı yazma) yüksek eşzamanlılık sağlayarak tek bir worker’ın bile yüzlerce isteği verimli bir şekilde yönetmesini mümkün kılar.
  * Veritabanı (PgBouncer & Replikasyon): Bağlantı havuzlama ve okuma replikaları sayesinde veritabanı yükü dengelenir ve performans artırılır.

### 6.2. Dayanıklılık ve Hata Yönetimi

  * Yeniden Deneme: HTTP hataları için 3 yeniden deneme, üstel geri çekilme (2^n saniye bekleme).
  * Rate Limiting: Sabit 0.5 saniye gecikme ile 1 istek/saniye.
  * Hata Günlükleme: Başarısız istekler `failed_scrapes` tablosuna, geçersiz veriler `validation_errors` tablolarına kaydedilir.
  * Kısmi Hatalar: Geçersiz veya hatalı veriler (`validation_errors` tablosuna kaydedilerek) ve scrape edilemeyen şubeler veya sayfalar (`failed_scrapes` tablosuna kaydedilerek) atlanır, ancak başarılı işlemler devam eder. Bu hatalar günlüklenir ve periyodik olarak incelenir.

### 6.3. İzleme ve Günlükleme

  * Yerel Günlükleme: Her scrape için başarı/hata sayıları ve süreler `logs/scrape_YYYY-MM-DD.log` dosyasına yazılır.
  * Metrikler: Şube başına başarı oranı, hata türleri (örn. timeout, geçersiz veri).
  * Uyarılar: Kritik hatalar (örn. %80’den az şube toplanırsa) konsola yazdırılır. Gelecekte e-posta uyarıları (`smtplib` ile).
  * Gelecek: Prometheus ve Grafana ile metrik görselleştirme (Faz 2).

### 6.4. Yedekleme

  * Haftalık PostgreSQL yedeklemeleri: `pg_dump -U postgres esn_pulse > backups/esn_pulse_YYYY-MM-DD.sql`.
  * Yerel yedekler ayrı bir klasörde saklanır. Gelecekte bulut yedekleri (örn. AWS S3).

-----

## 7. Gelecek Geliştirmeler (Out of Scope for Initial Version)

### Faz 2:

  * Web Arayüzü: FastAPI/Streamlit ile diğer şubelerin verilere erişimi (örn. şube bazlı sorgular, basit dashboardlar).
  * Hosting: Heroku (ücretsiz katman) veya AWS EC2.
  * Örnek: Şube istatistiklerini ve etkinlik detaylarını gösteren basit bir dashboard.

### Faz 3:

  * AI Destekli Etkinlik Planlayıcı: Kural tabanlı ve/veya Makine Öğrenimi destekli etkinlik öneri sistemi.
  * Amaç: Üye ve Erasmus katılımını artırmak, eksik nedenlerde (causes) etkinlik önerileri sunmak.
  * Gelişmiş Veri Analizi: Web tabanlı analiz paneli (Power BI/Tableau yerine).
  * Çok Dilli Destek: Platformlar farklı dillerde veri sunarsa, İngilizce dışındaki verilerin yönetimi.
  * Geri Bildirim Döngüsü: Her faz sonrası anketler (örn. Google Form) ile şubelerden geri bildirim toplanacak.

-----

## 8. Dokümantasyon ve Bakım

  * README.MD: Yerel kurulum (Docker Compose), çalıştırma (`python run_scraper.py`), ve veri sorgulama (`psql`) talimatları.
  * Bakım: Tek geliştirici (ESN Marmara) tarafından yönetilecek. Gelecekte ESN Türkiye web komitesine devredilebilir.
  * Eğitim: Teknik olmayan gönüllüler için 1 saatlik SQL/BI aracı eğitimi planlanacak.