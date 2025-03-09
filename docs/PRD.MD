# Proje Adı: ESN Pulse

## 1. Giriş

* **Amaç:** ESN Marmara'nın etkinliklerini daha yaratıcı, eğlenceli ve sıra dışı hale getirmek. Diğer ESN şubelerinin etkinliklerinden ilham alarak ve yapay zeka API'leri kullanarak yeni fikirler üretmek.
* **Hedef Kitle:** ESN Marmara'ya bağlı uluslararası öğrenciler ve gönüllüler.
* **Vizyon:** ESN Marmara'yı Türkiye'deki en yenilikçi ve ilgi çekici etkinliklere sahip ESN şubesi yapmak.

## 2. Hedefler

* Diğer ESN şubelerinin temel verilerini toplamak ve analiz etmek.
* Yapay zeka API'leri kullanarak yeni ve özgün etkinlik fikirleri üretmek.
* ESN Marmara'nın etkinlik portföyünü çeşitlendirmek ve zenginleştirmek.
* Uluslararası öğrencilerin katılımını ve memnuniyetini artırmak.
* ESN Marmara'nın kurumsal kimliğini kuvvetlendirmek.

## 3. Kapsam

* **Veri Toplama:** activities.esn.org adresinden diğer ESN şubelerinin temel verilerinin toplanması (şube bilgileri).
* **Veri Analizi:** Toplanan verilerin analiz edilerek trendlerin ve başarılı etkinliklerin belirlenmesi.
* **Etkinlik Fikirleri Üretimi:** Yapay zeka API'leri kullanarak ESN Marmara'ya özgü yeni ve yaratıcı etkinlik fikirlerinin üretilmesi.
* **Etkinlik Planlama:** Üretilen fikirlerin ESN Marmara'nın ihtiyaçlarına ve kaynaklarına göre uyarlanarak etkinlik planlarının oluşturulması.
* **Değerlendirme:** Yapılan etkinliklerin istatistiksel veriler ile değerlendirilerek kimlik oluşturma.

## 4. İş Akışı

1. **Plan:**
   * Diğer ESN şubelerinin temel verilerinin toplanması.
   * Verilerin temizlenmesi ve düzenlenmesi.
   * Yeni etkinlik fikirlerinin üretilmesi.
   * ESN Marmara'ya özel kimlik oluşturulması.
2. **Act:**
   * Etkinlik planlarının oluşturulması.
   * Etkinliklerin gerçekleştirilmesi.
   * Etkinlik verilerinin toplanması.
   * Etkinliklerin değerlendirilmesi ve iyileştirilmesi.

## 5. Veri Kaynakları

Proje, aşağıdaki URL'lerden veri toplamayı hedeflemektedir:

* **Şube Bilgileri (Organisation Details):**
    * `https://activities.esn.org/organisation/{sube_adi}`
    * Amaç: İlgili ESN şubesi hakkında genel bilgileri (şube adı, konumu, iletişim bilgileri vb.) toplamak.
* **Etkinlik Listesi (Activity List):**
    * `https://activities.esn.org/organisation/{sube_adi}/activities`
    * Amaç: Şubenin düzenlediği etkinliklerin ID'lerini (activity_id) listeleyerek detaylı etkinlik bilgilerini çekmek için bir kaynak sağlamak.
* **Etkinlik Detayları (Activity Details):**
    * `https://activities.esn.org/activity/{etkinlik_id}`
    * Amaç: Belirli bir etkinliğin detaylı bilgilerini (etkinlik başlığı, tarihi, konumu, açıklaması, katılımcı sayısı vb.) toplamak.
* **İstatistikler (Statistics):**
    * `https://activities.esn.org/organisation/{sube_adi}/statistics`
    * Amaç: Şubenin düzenlediği etkinliklere ilişkin istatistiksel verileri (toplam etkinlik sayısı, katılımcı sayıları, etkinlik türleri, nedenlere göre dağılım vb.) toplamak.

## 6. Veri Toplama ve İşleme

* Veriler, Python ve BeautifulSoup kütüphanesi kullanılarak web scraping yöntemiyle toplanacaktır.
* Toplanan veriler, PostgreSQL veritabanında saklanacaktır.
* Veri toplama işlemi düzenli aralıklarla (örneğin, günlük veya haftalık) otomatik olarak gerçekleştirilecektir.
* Veri temizleme ve dönüştürme işlemleri, verilerin tutarlılığını ve doğruluğunu sağlamak için yapılacaktır.

## 7. Veritabanı Şeması

* **Şubeler (Organisations) Tablosu:**
    * `organisation_id` (PK)
    * `organisation_name`
    * `activity_count`
    * `city_count`
    * `participant_count`
* **Etkinlikler (Activities) Tablosu:**
    * `activity_id` (PK)
    * `organisation_id` (FK)
    * `activity_title`
    * `activity_date`
    * `activity_city`
    * `activity_country`
    * `participant_count`
    * `activity_causes`
    * `activity_type`
    * `activity_goal`
    * `activity_description`
    * `sdg_goals`
    * `activity_objectives`
    * `activity_organiser`
* **İstatistikler (Statistics) Tablosu:**
    * `organisation_id` (FK)
    * `total_physical_activities`
    * `total_online_activities`
    * `local_students_participants`
    * `international_students_participants`
    * `coordinators_participants`
    * `total_participants`
    * `environmental_sustainability_activities`
    * `social_inclusion_activities`
    * `culture_activities`
    * `education_youth_activities`
    * `health_wellbeing_activities`
    * `skills_employability_activities`
    * `physical_activity_types`
    * `online_activity_types`

## 8. Kullanım Alanları

* ESN etkinliklerinin merkezi bir veritabanında toplanması.
* Etkinlik trendlerinin ve katılımcı demografisinin analiz edilmesi.
* ESN şubeleri arasında etkinlik karşılaştırması yapılması.
* ESN'in etkinliklerini daha iyi tanıtmak ve duyurmak için kullanılması.

## 9. Başarı Kriterleri

* ESN Marmara'nın etkinlik sayısının ve çeşitliliğinin artması.
* Etkinliklere katılan uluslararası öğrenci sayısının artması.
* Etkinliklerden elde edilen memnuniyet düzeyinin artması.
* ESN Marmara'nın sosyal medya ve diğer platformlarda görünürlüğünün artması.
* ESN Marmara'nın diğer şubelerce örnek gösterilmesi.

## 10. Gelecek Geliştirmeler

* Veri görselleştirme araçları ile istatistiklerin daha anlaşılır hale getirilmesi.
* Kullanıcıların etkinliklere göre arama ve filtreleme yapabileceği bir web arayüzü geliştirilmesi.
* Veri analizi ve makine öğrenimi teknikleri ile etkinlik tahminleri yapılması.
* Diğer ESN platformlarından veri toplama yeteneğinin eklenmesi.