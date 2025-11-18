import os
from celery import Celery

# Define a variável de ambiente padrão do Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Namespace='CELERY' significa que todas as configs do Celery no settings.py
# devem começar com CELERY_ (ex: CELERY_BROKER_URL)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carrega tasks de todos os 'tasks.py' dentro dos apps do Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')