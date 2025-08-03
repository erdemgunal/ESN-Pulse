"""
Activity Model - Etkinlik verilerini temsil eden Pydantic modeli

Bu model activities.esn.org'dan çekilen etkinlik bilgilerini doğrular ve yapılandırır.
"""

from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field, HttpUrl, validator


class ActivityModel(BaseModel):
    """
    ESN etkinlik verilerini temsil eden model.
    
    Attributes:
        id: Veritabanı primary key (auto-generated)
        event_slug: Benzersiz etkinlik tanımlayıcısı (örn. 'boat-party-20885')
        url: Etkinlik sayfası URL'si
        title: Etkinlik başlığı
        description: Etkinlik açıklaması
        start_date: Başlangıç tarihi
        end_date: Bitiş tarihi (optional)
        city: Etkinlik şehri
        country_code: Ülke kodu
        participants: Katılımcı sayısı
        activity_type: Etkinlik türü
        is_future_event: Gelecekteki etkinlik mi
        organisers: Düzenleyici şubeler
        causes: Etkinlik nedenleri
        sdgs: Sürdürülebilir Kalkınma Hedefleri
        objectives: Etkinlik hedefleri
        is_valid: Veri geçerliliği flag'i
    """
    
    # Database fields
    id: Optional[int] = Field(None, description="Database primary key")
    
    # Required fields
    event_slug: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Unique event identifier"
    )
    
    url: HttpUrl = Field(
        ...,
        description="Event page URL"
    )
    
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Event title"
    )
    
    description: str = Field(
        ...,
        min_length=1,
        description="Event description"
    )
    
    start_date: date = Field(
        ...,
        description="Event start date"
    )
    
    # Optional temporal fields
    end_date: Optional[date] = Field(
        None,
        description="Event end date"
    )
    
    # Location fields
    city: Optional[str] = Field(
        None,
        max_length=100,
        description="Event city"
    )
    
    country_code: Optional[str] = Field(
        None,
        max_length=10,
        description="Country code"
    )
    
    # Participation data
    participants: int = Field(
        default=0,
        ge=0,
        description="Total number of participants"
    )
    
    activity_type: Optional[str] = Field(
        None,
        max_length=100,
        description="Type of activity"
    )
    
    # Computed fields
    is_future_event: bool = Field(
        ...,
        description="Whether the event is in the future"
    )
    
    # Related data (Many-to-Many relationships)
    organisers: List[str] = Field(
        default_factory=list,
        description="List of organising sections"
    )
    
    causes: List[str] = Field(
        default_factory=list,
        description="List of activity causes"
    )
    
    sdgs: List[str] = Field(
        default_factory=list,
        description="List of Sustainable Development Goals"
    )
    
    objectives: List[str] = Field(
        default_factory=list,
        description="List of activity objectives"
    )
    
    # Data quality control
    is_valid: bool = Field(
        default=True,
        description="Data validation flag"
    )
    
    created_at: Optional[datetime] = Field(
        None,
        description="Record creation timestamp"
    )
    
    updated_at: Optional[datetime] = Field(
        None,
        description="Record update timestamp"
    )
    
    @validator('event_slug')
    def validate_event_slug(cls, v):
        """Validate event slug format."""
        if v:
            v = v.lower().strip()
            # Event slugs can contain letters, numbers, and hyphens
            if not v.replace('-', '').replace('_', '').isalnum():
                raise ValueError('Event slug must contain only letters, numbers, hyphens, and underscores')
        return v
    
    @validator('title')
    def validate_title(cls, v):
        """Validate event title."""
        if v:
            v = v.strip()
            # Remove extra whitespace
            v = ' '.join(v.split())
        return v
    
    @validator('description')
    def validate_description(cls, v):
        """Validate event description."""
        if v:
            v = v.strip()
            # Remove extra whitespace
            v = ' '.join(v.split())
            
            # Minimum length check
            if len(v) < 10:
                raise ValueError('Description must be at least 10 characters long')
        return v
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate end date is not before start date."""
        if v is not None and 'start_date' in values:
            start_date = values['start_date']
            if v < start_date:
                raise ValueError('End date cannot be before start date')
        return v
    
    @validator('country_code')
    def validate_country_code(cls, v):
        """Validate country code format."""
        if v:
            v = v.upper().strip()
            # Basic validation - should be 2-3 uppercase letters
            if len(v) in [2, 3] and v.isalpha():
                return v
            raise ValueError('Country code must be 2-3 uppercase letters')
        return v
    
    @validator('participants')
    def validate_participants(cls, v):
        """Validate participant count."""
        if v < 0:
            raise ValueError('Participant count cannot be negative')
        if v > 10000:  # Reasonable upper limit
            raise ValueError('Participant count seems unreasonably high')
        return v
    
    @validator('organisers', 'causes', 'sdgs', 'objectives')
    def validate_lists(cls, v):
        """Validate list fields."""
        if v is None:
            return []
        
        # Remove empty strings and duplicates
        cleaned = []
        for item in v:
            if isinstance(item, str) and item.strip():
                cleaned_item = item.strip()
                if cleaned_item not in cleaned:
                    cleaned.append(cleaned_item)
        
        return cleaned
    
    @validator('is_future_event', always=True)
    def validate_is_future_event(cls, v, values):
        """Auto-calculate is_future_event based on start_date."""
        if 'start_date' in values:
            start_date = values['start_date']
            if start_date:
                today = date.today()
                return start_date > today
        return v
    
    class Config:
        """Pydantic config."""
        
        # JSON schema extra information
        json_schema_extra = {
            "example": {
                "event_slug": "boat-party-20885",
                "url": "https://activities.esn.org/activity/boat-party-20885",
                "title": "Boat Party",
                "description": "ESNers were entertained with a variety of content and had a look at the Bosphorus in the evening.",
                "start_date": "2023-11-08",
                "end_date": "2023-11-08",
                "city": "Istanbul",
                "country_code": "TR",
                "participants": 160,
                "activity_type": "Game or Social Activity",
                "is_future_event": False,
                "organisers": ["ESN Yıldız"],
                "causes": ["Culture", "Education & Youth"],
                "sdgs": ["SDG 3", "SDG 4"],
                "objectives": ["Mental Health & Well-Being"],
                "is_valid": True
            }
        }
        
        # Validation settings
        validate_assignment = True
        str_strip_whitespace = True
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }
        
        # Allow field aliases
        validate_by_name = True


class ActivityCreateModel(BaseModel):
    """Model for creating new activities (without auto-generated fields)."""
    
    event_slug: str = Field(..., min_length=1, max_length=255)
    url: HttpUrl
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    start_date: date
    end_date: Optional[date] = None
    city: Optional[str] = Field(None, max_length=100)
    country_code: Optional[str] = Field(None, max_length=10)
    participants: int = Field(default=0, ge=0)
    activity_type: Optional[str] = Field(None, max_length=100)
    organisers: List[str] = Field(default_factory=list)
    causes: List[str] = Field(default_factory=list)
    sdgs: List[str] = Field(default_factory=list)
    objectives: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_slug": "boat-party-20885",
                "url": "https://activities.esn.org/activity/boat-party-20885",
                "title": "Boat Party",
                "description": "ESNers were entertained with a variety of content and had a look at the Bosphorus in the evening.",
                "start_date": "2023-11-08",
                "city": "Istanbul",
                "country_code": "TR",
                "participants": 160,
                "activity_type": "Game or Social Activity",
                "organisers": ["ESN Yıldız"],
                "causes": ["Culture"]
            }
        }


class ActivityUpdateModel(BaseModel):
    """Model for updating existing activities (all fields optional)."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    city: Optional[str] = Field(None, max_length=100)
    country_code: Optional[str] = Field(None, max_length=10)
    participants: Optional[int] = Field(None, ge=0)
    activity_type: Optional[str] = Field(None, max_length=100)
    organisers: Optional[List[str]] = None
    causes: Optional[List[str]] = None
    sdgs: Optional[List[str]] = None
    objectives: Optional[List[str]] = None
    is_valid: Optional[bool] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "participants": 200,
                "activity_type": "Social Activity",
                "is_valid": True
            }
        }


class ActivitySearchModel(BaseModel):
    """Model for activity search parameters."""
    
    title: Optional[str] = None
    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None
    city: Optional[str] = None
    country_code: Optional[str] = None
    activity_type: Optional[str] = None
    min_participants: Optional[int] = Field(None, ge=0)
    max_participants: Optional[int] = Field(None, ge=0)
    is_future_event: Optional[bool] = None
    organisers: Optional[List[str]] = None
    causes: Optional[List[str]] = None
    sdgs: Optional[List[str]] = None
    is_valid: Optional[bool] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "start_date_from": "2023-01-01",
                "start_date_to": "2023-12-31",
                "country_code": "TR",
                "activity_type": "Social Activity",
                "min_participants": 50,
                "is_future_event": False
            }
        } 