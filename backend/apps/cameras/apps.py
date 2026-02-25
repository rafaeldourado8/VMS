from django.apps import AppConfig

class CamerasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.cameras"
    verbose_name = "Gerenciamento de Câmeras"

    def ready(self):
        import apps.cameras.signals
        
        # Auto-provision em background
        import threading
        threading.Thread(target=self._auto_provision, daemon=True).start()
    
    def _auto_provision(self):
        import time
        import httpx
        time.sleep(5)  # Aguarda Django iniciar
        
        try:
            from apps.cameras.models import Camera
            cameras = Camera.objects.filter(status='online')
            if cameras.count() == 0:
                return
            
            # Aguarda streaming
            for _ in range(10):
                try:
                    if httpx.get('http://streaming:8001/health', timeout=3).status_code == 200:
                        break
                except:
                    pass
                time.sleep(2)
            else:
                return
            
            # Provisiona
            with httpx.Client(timeout=30.0) as client:
                for camera in cameras:
                    try:
                        client.post(
                            'http://streaming:8001/cameras/provision',
                            json={
                                'camera_id': camera.id,
                                'rtsp_url': camera.stream_url,
                                'name': camera.name,
                                'enabled': True,
                                'on_demand': True
                            }
                        )
                    except:
                        pass
                    time.sleep(1)
        except:
            pass