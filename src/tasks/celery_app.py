"""
ESN PULSE Celery Application

Bu modül, ESN PULSE projesinin Celery görev yönetimini sağlar.
Scraper görevlerini koordine eder ve bağımlılıkları yönetir.
"""

import os
from celery import Celery
from celery.schedules import crontab

from src.config import settings

# Celery app oluştur
celery_app = Celery(
    'esn_pulse',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        'src.tasks.accounts_tasks',
        'src.tasks.activities_tasks'
    ]
)

# Celery ayarları
celery_app.conf.update(
    # Task ayarları
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Worker ayarları
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    worker_max_memory_per_child=200000,  # 200MB
    
    # Task yürütme ayarları
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=3600,  # 1 saat
    task_soft_time_limit=3300,  # 55 dakika
    
    # Retry ayarları
    task_default_retry_delay=300,  # 5 dakika
    task_max_retries=3,
    
    # Beat ayarları (zamanlanmış görevler)
    beat_schedule={
        'accounts-scraper-monthly': {
            'task': 'src.tasks.accounts_tasks.run_accounts_scraper',
            'schedule': crontab(day_of_month='1', hour='0', minute='0'),  # Her ayın 1'i saat 00:00'da
        },
        'activities-scraper-weekly': {
            'task': 'src.tasks.activities_tasks.run_activities_scraper',
            'schedule': crontab(day_of_week='monday', hour='1', minute='0'),  # Her Pazartesi saat 01:00'da
        },
    }
)

# Celery sinyalleri
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Periyodik görevleri yapılandır."""
    # Burada ek periyodik görevler eklenebilir
    pass

@celery_app.task(bind=True)
def debug_task(self):
    """Debug için test görevi."""
    print(f'Request: {self.request!r}') 