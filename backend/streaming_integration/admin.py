"""
Admin customizado com ações de streaming. (OBSOLETO PÓS-MEDIAMTX)
"""

from django.contrib import admin
from django.contrib import messages
# from .services import StreamingService # Obsoleto


class StreamingAdminMixin:
    """
    CLASSE OBSOLETA - DEPRECADA PELA MIGRAÇÃO PARA O MEDIAMTX.
    
    As ações de 'start_streams', 'stop_streams' e 'check_stream_status'
    não são mais válidas, pois o MediaMTX gere os streams sob demanda.
    
    Este Mixin é mantido (vazio) para evitar erros em Admin.
    """
    
    # actions = ['start_streams', 'stop_streams', 'check_stream_status']
    actions = [] # Remove as ações
    
    # Todos os métodos (start_streams, stop_streams, check_stream_status)
    # foram removidos.