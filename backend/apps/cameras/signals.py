from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Camera
import logging

logger = logging.getLogger(__name__)

# Signals desabilitados - o provisionamento é feito pelo CameraService
# para evitar duplicação e melhor controle de erros

# @receiver(post_save, sender=Camera)
# def manage_external_services(sender, instance, created, **kwargs):
#     pass

# @receiver(pre_delete, sender=Camera)
# def cleanup_external_services(sender, instance, **kwargs):
#     pass