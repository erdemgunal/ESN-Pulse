"""
Country Model - Ülke verilerini temsil eden Pydantic modeli

Bu model accounts.esn.org'dan çekilen ülke bilgilerini doğrular ve yapılandırır.
"""

from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, validator


class CountryModel(BaseModel):
    """
    ESN ülke verilerini temsil eden model.
    
    Attributes:
        country_code: 2 harfli ülke kodu (örn. 'TR', 'DE')
        name: Ülke adı (örn. 'Turkey', 'Germany')
        slug: URL-friendly ülke slug'ı (örn. 'turkey', 'germany')
        url: accounts.esn.org'daki ülke sayfası URL'si
        section_count: Ülkedeki toplam şube sayısı
    """
    
    country_code: str = Field(
        ...,
        min_length=2,
        max_length=10,
        description="2-letter ISO country code"
    )
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Country name"
    )
    
    slug: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="URL-friendly country slug"
    )
    
    url: HttpUrl = Field(
        ...,
        description="Country page URL on accounts.esn.org"
    )
    
    section_count: int = Field(
        default=0,
        ge=0,
        description="Total number of sections in this country"
    )
    
    @validator('country_code')
    def validate_country_code(cls, v):
        """Validate country code format."""
        if not v.isupper():
            v = v.upper()
        
        # Basic validation - should be 2 uppercase letters
        if len(v) == 2 and v.isalpha():
            return v
        
        raise ValueError('Country code must be 2 uppercase letters')
    
    @validator('slug')
    def validate_slug(cls, v):
        """Validate slug format."""
        # Convert to lowercase and remove special characters
        v = v.lower().strip()
        
        # Basic slug validation
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug must contain only letters, numbers, hyphens, and underscores')
        
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """Validate country name."""
        v = v.strip()
        
        if not v:
            raise ValueError('Country name cannot be empty')
        
        # Remove extra whitespace
        v = ' '.join(v.split())
        
        return v
    
    class Config:
        """Pydantic config."""
        
        # JSON schema extra information
        json_schema_extra = {
            "example": {
                "country_code": "TR",
                "name": "Turkey",
                "slug": "turkey",
                "url": "https://accounts.esn.org/country/tr",
                "section_count": 42
            }
        }
        
        # Validation settings
        validate_assignment = True
        str_strip_whitespace = True
        
        # Allow field aliases
        validate_by_name = True


class CountryCreateModel(BaseModel):
    """Model for creating new countries (without auto-generated fields)."""
    
    country_code: str = Field(..., min_length=2, max_length=10)
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    url: HttpUrl
    
    class Config:
        json_schema_extra = {
            "example": {
                "country_code": "TR",
                "name": "Turkey", 
                "slug": "turkey",
                "url": "https://accounts.esn.org/country/tr"
            }
        }


class CountryUpdateModel(BaseModel):
    """Model for updating existing countries (all fields optional)."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    url: Optional[HttpUrl] = None
    section_count: Optional[int] = Field(None, ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Turkey",
                "section_count": 45
            }
        } 