"""
ESN PULSE Exceptions

Bu modül, ESN PULSE projesinin özel hata sınıflarını içerir.
"""

class ESNPulseError(Exception):
    """ESN PULSE temel hata sınıfı."""
    pass

class ScrapingError(ESNPulseError):
    """Scraping sırasında oluşan hatalar için temel sınıf."""
    
    def __init__(self, message: str, url: str = None, status_code: int = None):
        self.url = url
        self.status_code = status_code
        super().__init__(message)

class ValidationError(ESNPulseError):
    """Veri doğrulama hataları için temel sınıf."""
    
    def __init__(self, message: str, field_name: str = None, raw_data: dict = None):
        self.field_name = field_name
        self.raw_data = raw_data
        super().__init__(message)

class RateLimitError(ScrapingError):
    """Rate limit aşıldığında fırlatılan hata."""
    pass

class CloudflareError(ScrapingError):
    """Cloudflare koruması tespit edildiğinde fırlatılan hata."""
    pass

class NetworkError(ScrapingError):
    """Ağ bağlantısı hataları için temel sınıf."""
    pass

class TimeoutError(NetworkError):
    """İstek zaman aşımına uğradığında fırlatılan hata."""
    pass

class DatabaseError(ESNPulseError):
    """Veritabanı hataları için temel sınıf."""
    pass

class ConfigurationError(ESNPulseError):
    """Konfigürasyon hataları için temel sınıf."""
    pass 