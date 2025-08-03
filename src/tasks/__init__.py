"""
ESN PULSE Tasks Package

Bu paket, ESN PULSE projesinin Celery görevlerini içerir.
"""

from .celery_app import celery_app
from .accounts_tasks import run_accounts_scraper
from .activities_tasks import run_activities_scraper

__all__ = [
    'celery_app',
    'run_accounts_scraper',
    'run_activities_scraper'
] 