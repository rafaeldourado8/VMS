"""
Views para integração com streaming. (OBSOLETO PÓS-MEDIAMTX)
Mixin para adicionar funcionalidades de streaming a ViewSets existentes.
"""

import logging
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
# O serviço não é mais usado para iniciar/parar streams
# from .services import StreamingService 

logger = logging.getLogger(__name__)


class StreamingMixin:
    """
    CLASSE OBSOLETA - DEPRECADA PELA MIGRAÇÃO PARA O MEDIAMTX.
    
    O Django não é mais responsável por iniciar ou parar streams.
    Este Mixin é mantido (vazio) para evitar erros de importação
    nos ViewSets que o utilizam (ex: CameraViewSet).
    """
    
    # As ações @action(detail=True...) 'start-stream', 'stop-stream', 
    # e 'stream-status' foram removidas.
    
    pass