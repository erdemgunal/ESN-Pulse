"""
ESN PULSE Date Parser

Bu modül, ESN PULSE projesinin tarih ayrıştırma fonksiyonlarını içerir.
"""

import re
from datetime import datetime, date
from typing import Optional, Tuple

import pytz
from dateutil.parser import parse as dateutil_parse

def parse_event_date(date_str: str) -> date:
    """Etkinlik tarihini ayrıştırır.
    
    Args:
        date_str: Ayrıştırılacak tarih stringi (örn. "2023-11-08")
    
    Returns:
        Ayrıştırılmış tarih
    
    Raises:
        ValueError: Tarih formatı geçersizse
    """
    try:
        return dateutil_parse(date_str).date()
    except (ValueError, TypeError) as e:
        raise ValueError(f"Geçersiz tarih formatı: {date_str}") from e

def parse_event_date_range(date_range_str: str) -> Tuple[date, Optional[date]]:
    """Etkinlik tarih aralığını ayrıştırır.
    
    Args:
        date_range_str: Ayrıştırılacak tarih aralığı stringi
                       (örn. "2023-11-08" veya "2023-11-08 - 2023-11-10")
    
    Returns:
        (başlangıç_tarihi, bitiş_tarihi) tuple'ı.
        Bitiş tarihi belirtilmemişse None döner.
    
    Raises:
        ValueError: Tarih formatı geçersizse
    """
    # Tarih aralığını ayır
    parts = [p.strip() for p in date_range_str.split("-")]
    
    # Tek tarih varsa
    if len(parts) == 1:
        start_date = parse_event_date(parts[0])
        return start_date, None
    
    # Tarih aralığı varsa
    if len(parts) == 2:
        start_date = parse_event_date(parts[0])
        end_date = parse_event_date(parts[1])
        
        # Bitiş tarihi başlangıç tarihinden önce olamaz
        if end_date < start_date:
            raise ValueError(
                f"Bitiş tarihi ({end_date}) başlangıç tarihinden ({start_date}) önce olamaz"
            )
        
        return start_date, end_date
    
    raise ValueError(f"Geçersiz tarih aralığı formatı: {date_range_str}")

def is_future_event(event_date: date) -> bool:
    """Etkinliğin gelecekte olup olmadığını kontrol eder.
    
    Args:
        event_date: Kontrol edilecek tarih
    
    Returns:
        True: Etkinlik gelecekte
        False: Etkinlik geçmişte
    """
    return event_date >= date.today()

def format_date(d: date) -> str:
    """Tarihi ISO formatına çevirir.
    
    Args:
        d: Formatlanacak tarih
    
    Returns:
        ISO formatında tarih stringi (YYYY-MM-DD)
    """
    return d.isoformat()

def parse_timestamp(timestamp_str: str) -> datetime:
    """Zaman damgasını ayrıştırır.
    
    Args:
        timestamp_str: Ayrıştırılacak zaman damgası stringi
                      (örn. "2023-11-08T15:30:00Z")
    
    Returns:
        Ayrıştırılmış zaman damgası (UTC)
    
    Raises:
        ValueError: Zaman damgası formatı geçersizse
    """
    try:
        dt = dateutil_parse(timestamp_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=pytz.UTC)
        return dt
    except (ValueError, TypeError) as e:
        raise ValueError(f"Geçersiz zaman damgası formatı: {timestamp_str}") from e 