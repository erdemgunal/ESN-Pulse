"""
ESN PULSE Slug Generator

Bu modül, ESN PULSE projesinin slug oluşturma fonksiyonlarını içerir.
"""

import re
from typing import Optional

from slugify import slugify

def generate_activities_slug(section_name: str) -> str:
    """activities.esn.org için şube slug'ı oluşturur.
    
    Args:
        section_name: Şube adı (örn. "ESN METU")
    
    Returns:
        Slug (örn. "esn-metu")
    """
    # Şube adını küçük harfe çevir
    name = section_name.lower()
    
    # "esn" prefix'ini kontrol et
    if not name.startswith("esn"):
        name = f"esn {name}"
    
    # Slug oluştur
    return slugify(name)

def generate_accounts_slug(section_name: str, country_code: str) -> str:
    """accounts.esn.org için şube slug'ı oluşturur.
    
    Args:
        section_name: Şube adı (örn. "ESN METU")
        country_code: Ülke kodu (örn. "TR")
    
    Returns:
        Slug (örn. "tr-anka-met")
    """
    # Şube adını küçük harfe çevir
    name = section_name.lower()
    
    # "esn" prefix'ini kaldır
    name = re.sub(r"^esn\s+", "", name)
    
    # Şehir ve üniversite kodlarını çıkar
    parts = name.split()
    if len(parts) >= 2:
        city = parts[0][:4]  # İlk 4 harf
        uni = parts[1][:3]   # İlk 3 harf
        slug = f"{country_code.lower()}-{city}-{uni}"
    else:
        # Tek kelimeyse tamamını al
        slug = f"{country_code.lower()}-{name}"
    
    return slugify(slug)

def validate_activities_slug(slug: str) -> bool:
    """activities.esn.org slug'ının geçerli olup olmadığını kontrol eder.
    
    Args:
        slug: Kontrol edilecek slug
    
    Returns:
        True: Slug geçerli
        False: Slug geçersiz
    """
    # Boş veya None olamaz
    if not slug:
        return False
    
    # "esn" ile başlamalı
    if not slug.startswith("esn-"):
        return False
    
    # Sadece küçük harf, rakam ve tire içermeli
    if not re.match(r"^[a-z0-9-]+$", slug):
        return False
    
    # En az 5 karakter olmalı (esn- + en az 1 karakter)
    if len(slug) < 5:
        return False
    
    return True

def validate_accounts_slug(slug: str, country_code: Optional[str] = None) -> bool:
    """accounts.esn.org slug'ının geçerli olup olmadığını kontrol eder.
    
    Args:
        slug: Kontrol edilecek slug
        country_code: Ülke kodu (opsiyonel)
    
    Returns:
        True: Slug geçerli
        False: Slug geçersiz
    """
    # Boş veya None olamaz
    if not slug:
        return False
    
    # Sadece küçük harf, rakam ve tire içermeli
    if not re.match(r"^[a-z0-9-]+$", slug):
        return False
    
    # Ülke kodu verilmişse kontrol et
    if country_code:
        if not slug.startswith(country_code.lower()):
            return False
    
    # En az 3 parçadan oluşmalı (ülke-şehir-üni)
    parts = slug.split("-")
    if len(parts) < 3:
        return False
    
    return True 