from django.core.management.base import BaseCommand
from infrastructure.messaging.rabbitmq_consumer import start_rabbitmq_consumer

class Command(BaseCommand):
    help = 'Start RabbitMQ consumer for detections'

    def handle(self, *args, **options):
        self.stdout.write('Starting RabbitMQ consumer...')
        start_rabbitmq_consumer()
