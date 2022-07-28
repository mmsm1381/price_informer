import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'price_informer.settings')

app = Celery('price_informer')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
