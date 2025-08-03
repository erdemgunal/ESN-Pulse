"""
Section Model - Şube verilerini temsil eden Pydantic modeli

Bu model accounts.esn.org'dan çekilen şube bilgilerini doğrular ve yapılandırır.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, HttpUrl, EmailStr, validator, Json


class SectionModel(BaseModel):
    """
    ESN şube verilerini temsil eden model.
    
    Attributes:
        id: Veritabanı primary key (auto-generated)
        country_code: Bağlı olduğu ülkenin kodu
        name: Şube adı (örn. 'ESN METU', 'ESN Yıldız')
        accounts_platform_slug: accounts.esn.org'daki slug
        activities_platform_slug: activities.esn.org'daki slug
        accounts_url: accounts.esn.org'daki tam URL
        activities_url: activities.esn.org'daki tam URL
        city: Şehir adı
        address: Tam adres
        email: İletişim e-postası
        website: Web sitesi URL'si
        university_name: Üniversite adı
        longitude: GPS boylam koordinatı
        latitude: GPS enlem koordinatı
        social_media: Sosyal medya linkleri (JSON)
        logo_url: Logo resmi URL'si
        can_scrape_activities: Etkinlik verilerinin çekilebilir olup olmadığı
        last_validated_activities_slug: Son slug doğrulama zamanı
        last_scraped: Son scraping zamanı
    """
    
    # Database fields
    id: Optional[int] = Field(None, description="Database primary key")
    
    # Required fields
    country_code: str = Field(
        ...,
        max_length=10,
        description="Country code (foreign key)"
    )
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Section name"
    )
    
    accounts_platform_slug: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Unique slug on accounts platform"
    )
    
    # Platform-specific fields
    activities_platform_slug: Optional[str] = Field(
        None,
        max_length=255,
        description="Slug on activities platform"
    )
    
    accounts_url: Optional[HttpUrl] = Field(
        None,
        description="Full URL on accounts platform"
    )
    
    activities_url: Optional[HttpUrl] = Field(
        None,
        description="Full URL on activities platform"
    )
    
    # Contact and location information
    city: Optional[str] = Field(
        None,
        max_length=100,
        description="City name"
    )
    
    address: Optional[str] = Field(
        None,
        description="Full address"
    )
    
    email: Optional[EmailStr] = Field(
        None,
        description="Contact email"
    )
    
    website: Optional[HttpUrl] = Field(
        None,
        description="Official website URL"
    )
    
    university_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Associated university name"
    )
    
    # Geographic coordinates
    longitude: Optional[Decimal] = Field(
        None,
        max_digits=9,
        decimal_places=6,
        description="GPS longitude coordinate"
    )
    
    latitude: Optional[Decimal] = Field(
        None,
        max_digits=9,
        decimal_places=6,
        description="GPS latitude coordinate"
    )
    
    # Social media and branding
    social_media: Optional[Dict[str, str]] = Field(
        None,
        description="Social media links as JSON object"
    )
    
    logo_url: Optional[str] = Field(
        None,
        description="Logo image URL"
    )
    
    # Scraping control flags
    can_scrape_activities: Optional[bool] = Field(
        None,
        description="Whether activities can be scraped for this section"
    )
    
    last_validated_activities_slug: Optional[datetime] = Field(
        None,
        description="Last time activities slug was validated"
    )
    
    last_scraped: Optional[datetime] = Field(
        None,
        description="Last time this section was scraped"
    )
    
    @validator('country_code')
    def validate_country_code(cls, v):
        """Validate country code format."""
        if v:
            v = v.upper().strip()
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """Validate section name."""
        if v:
            v = v.strip()
            # Remove extra whitespace
            v = ' '.join(v.split())
        return v
    
    @validator('accounts_platform_slug')
    def validate_accounts_slug(cls, v):
        """Validate accounts platform slug."""
        if v:
            v = v.lower().strip()
            # Basic slug validation
            if not v.replace('-', '').replace('_', '').isalnum():
                raise ValueError('Accounts slug must contain only letters, numbers, hyphens, and underscores')
        return v
    
    @validator('activities_platform_slug')
    def validate_activities_slug(cls, v):
        """Validate activities platform slug."""
        if v:
            v = v.lower().strip()
            # Basic slug validation
            if not v.replace('-', '').replace('_', '').isalnum():
                raise ValueError('Activities slug must contain only letters, numbers, hyphens, and underscores')
        return v
    
    @validator('longitude')
    def validate_longitude(cls, v):
        """Validate longitude coordinate."""
        if v is not None:
            if not (-180 <= float(v) <= 180):
                raise ValueError('Longitude must be between -180 and 180')
        return v
    
    @validator('latitude')
    def validate_latitude(cls, v):
        """Validate latitude coordinate."""
        if v is not None:
            if not (-90 <= float(v) <= 90):
                raise ValueError('Latitude must be between -90 and 90')
        return v
    
    @validator('social_media')
    def validate_social_media(cls, v):
        """Validate social media JSON structure."""
        if v is not None:
            # Ensure it's a dictionary with string keys and values
            if not isinstance(v, dict):
                raise ValueError('Social media must be a dictionary')
            
            for key, value in v.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise ValueError('Social media keys and values must be strings')
        
        return v
    
    class Config:
        """Pydantic config."""
        
        # JSON schema extra information
        json_schema_extra = {
            "example": {
                "country_code": "TR",
                "name": "ESN METU",
                "accounts_platform_slug": "tr-anka-met",
                "activities_platform_slug": "esn-metu",
                "accounts_url": "https://accounts.esn.org/section/tr-anka-met",
                "activities_url": "https://activities.esn.org/organisation/esn-metu",
                "city": "Ankara",
                "address": "Üniversiteler Mahallesi, Dumlupınar Bulvarı No:1",
                "email": "esnmetu@metu.edu.tr",
                "website": "https://metu.esnturkey.org/",
                "university_name": "Middle East Technical University",
                "longitude": 32.7767,
                "latitude": 39.8935,
                "social_media": {
                    "facebook": "https://facebook.com/esnmetu",
                    "instagram": "https://instagram.com/esnmetu"
                },
                "logo_url": "/sites/default/files/styles/medium/public/organisation-logos/esn/TR-ANKA-MET.png.webp",
                "can_scrape_activities": True
            }
        }
        
        # Validation settings
        validate_assignment = True
        str_strip_whitespace = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
        # Allow field aliases
        validate_by_name = True


class SectionCreateModel(BaseModel):
    """Model for creating new sections (without auto-generated fields)."""
    
    country_code: str = Field(..., max_length=10)
    name: str = Field(..., min_length=1, max_length=255)
    accounts_platform_slug: str = Field(..., min_length=1, max_length=255)
    activities_platform_slug: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None
    university_name: Optional[str] = Field(None, max_length=255)
    
    class Config:
        json_schema_extra = {
            "example": {
                "country_code": "TR",
                "name": "ESN METU",
                "accounts_platform_slug": "tr-anka-met",
                "activities_platform_slug": "esn-metu",
                "city": "Ankara",
                "email": "esnmetu@metu.edu.tr"
            }
        }


class SectionUpdateModel(BaseModel):
    """Model for updating existing sections (all fields optional)."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    activities_platform_slug: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None
    university_name: Optional[str] = Field(None, max_length=255)
    longitude: Optional[Decimal] = None
    latitude: Optional[Decimal] = None
    social_media: Optional[Dict[str, str]] = None
    logo_url: Optional[str] = None
    can_scrape_activities: Optional[bool] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "city": "Ankara",
                "university_name": "Middle East Technical University",
                "can_scrape_activities": True
            }
        } 