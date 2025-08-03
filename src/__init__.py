"""
ESN PULSE - ESN Network Data Scraper & Analytics Platform

Bu paket, ESN (Erasmus Student Network) ağındaki 46 ülke ve 517 şubenin 
verilerini otomatik olarak toplayan, işleyen ve analiz için hazır hale 
getiren bir veri scraping ve analitik platformudur.

Modüller:
- scrapers: AccountsScraper ve ActivitiesAndStatisticsScraper
- models: Pydantic veri modelleri
- database: Veritabanı şemaları ve işlemleri
- tasks: Celery görevleri
- utils: Yardımcı fonksiyonlar
- cli: Komut satırı arayüzü
"""

__version__ = "1.0.0"
__author__ = "ESN PULSE Team"
__email__ = "esnpulse@example.com"

# Package level imports
from .config import settings 