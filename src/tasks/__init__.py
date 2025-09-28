"""
ESN PULSE Tasks Package

Bu paket, ESN PULSE projesinin Celery görevlerini içerir.
"""

from .celery_app import celery_app

__all__ = [
    'celery_app',
] 