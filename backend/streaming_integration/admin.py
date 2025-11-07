"""
Admin customizado com ações de streaming.
"""

from django.contrib import admin
from django.contrib import messages
from .services import StreamingService


class StreamingAdminMixin:
    """
    Mixin para adicionar ações de streaming ao Django Admin.
    
    Uso:
        @admin.register(Camera)
        class CameraAdmin(StreamingAdminMixin, admin.ModelAdmin):
            pass
    """
    
    actions = ['start_streams', 'stop_streams', 'check_stream_status']
    
    def start_streams(self, request, queryset):
        """Inicia streams para câmeras selecionadas."""
        success_count = 0
        for camera in queryset:
            stream_id = StreamingService.create_stream_for_camera(camera)
            if stream_id:
                success_count += 1
        
        self.message_user(
            request,
            f'{success_count} stream(s) iniciado(s) com sucesso.',
            messages.SUCCESS
        )
    start_streams.short_description = "Iniciar streams selecionados"
    
    def stop_streams(self, request, queryset):
        """Para streams para câmeras selecionadas."""
        success_count = 0
        for camera in queryset:
            if StreamingService.delete_stream_for_camera(camera):
                success_count += 1
        
        self.message_user(
            request,
            f'{success_count} stream(s) parado(s) com sucesso.',
            messages.SUCCESS
        )
    stop_streams.short_description = "Parar streams selecionados"
    
    def check_stream_status(self, request, queryset):
        """Verifica status dos streams."""
        for camera in queryset:
            status = StreamingService.get_stream_status(camera)
            if status:
                self.message_user(
                    request,
                    f'Câmera {camera}: {status.get("status")} - FPS: {status.get("fps")}',
                    messages.INFO
                )
            else:
                self.message_user(
                    request,
                    f'Câmera {camera}: Stream não encontrado',
                    messages.WARNING
                )
    check_stream_status.short_description = "Verificar status dos streams"