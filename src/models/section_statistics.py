"""
ESN PULSE Section Statistics Model

Bu modül, şube istatistiklerinin veri modellerini içerir.
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator

class SectionOverallStatisticsModel(BaseModel):
    """Şubenin genel istatistikleri."""
    
    section_id: int
    physical_activities: int = Field(default=0, ge=0)
    online_activities: int = Field(default=0, ge=0)
    total_local_students: int = Field(default=0, ge=0)
    total_international_students: int = Field(default=0, ge=0)
    total_coordinators: int = Field(default=0, ge=0)
    scraped_at: datetime = Field(default_factory=datetime.now)

class SectionCauseStatisticsModel(BaseModel):
    """Şubenin neden bazlı istatistikleri."""
    
    section_id: int
    cause_name: str
    total_count: int = Field(default=0, ge=0)
    physical_count: int = Field(default=0, ge=0)
    online_count: int = Field(default=0, ge=0)
    scraped_at: datetime = Field(default_factory=datetime.now)

class SectionTypeStatisticsModel(BaseModel):
    """Şubenin etkinlik türü bazlı istatistikleri."""
    
    section_id: int
    activity_type: str
    physical_count: int = Field(default=0, ge=0)
    online_count: int = Field(default=0, ge=0)
    scraped_at: datetime = Field(default_factory=datetime.now)

class SectionParticipantStatisticsModel(BaseModel):
    """Şubenin katılımcı türü bazlı istatistikleri."""
    
    section_id: int
    participant_type: str
    physical_count: int = Field(default=0, ge=0)
    online_count: int = Field(default=0, ge=0)
    scraped_at: datetime = Field(default_factory=datetime.now)

class SectionStatisticsModel(BaseModel):
    """Şubenin tüm istatistikleri."""
    
    section_id: int
    overall: SectionOverallStatisticsModel
    causes: List[SectionCauseStatisticsModel]
    types: List[SectionTypeStatisticsModel]
    participants: List[SectionParticipantStatisticsModel]
    scraped_at: datetime = Field(default_factory=datetime.now)
    
    @validator("causes")
    def validate_causes(cls, v):
        """Neden istatistiklerini doğrula."""
        if not v:
            raise ValueError("En az bir neden istatistiği olmalı")
        return v
    
    @validator("types")
    def validate_types(cls, v):
        """Tür istatistiklerini doğrula."""
        if not v:
            raise ValueError("En az bir tür istatistiği olmalı")
        return v
    
    @validator("participants")
    def validate_participants(cls, v):
        """Katılımcı istatistiklerini doğrula."""
        if not v:
            raise ValueError("En az bir katılımcı istatistiği olmalı")
        return v 