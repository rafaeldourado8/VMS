#!/usr/bin/env python
import os
import django
from threading import Thread

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from infrastructure.rabbitmq.detection_consumer import start_detection_consumer

if __name__ == '__main__':
    consumer_thread = Thread(target=start_detection_consumer, daemon=True)
    consumer_thread.start()
    print("Detection consumer started in background")
    consumer_thread.join()
