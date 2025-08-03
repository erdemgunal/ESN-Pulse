"""
ESN PULSE Lookup Models

Bu modül, etkinlik nedenleri, SDG'ler ve hedefler gibi
lookup tablolarının veri modellerini içerir.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

class ActivityCause(BaseModel):
    """Etkinlik nedeni modeli."""
    
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=100)
    created_at: datetime = Field(default_factory=datetime.now)

class SDG(BaseModel):
    """Sürdürülebilir Kalkınma Hedefi (SDG) modeli."""
    
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class Objective(BaseModel):
    """Etkinlik hedefi modeli."""
    
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=200)
    created_at: datetime = Field(default_factory=datetime.now) 