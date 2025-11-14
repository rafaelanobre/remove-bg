import os
import ssl

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'remove_bg.settings')

app = Celery('remove_bg')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Enable SSL only for TLS connections (rediss://)
broker_url = os.getenv('CELERY_BROKER_URL', '')
use_ssl = broker_url.startswith('rediss://')

ssl_config = (
    {
        'ssl_cert_reqs': ssl.CERT_REQUIRED,
    }
    if use_ssl
    else None
)

app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    result_expires=3600,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    timezone='UTC',
    enable_utc=True,
    broker_use_ssl=ssl_config,
    redis_backend_use_ssl=ssl_config,
)

app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
