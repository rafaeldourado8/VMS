# Sprint 3: Cameras (CRUD)

## 🎯 Objetivo
Implementar CRUD completo de câmeras com suporte RTSP (LPR) e RTMP (gravação).

## 📋 Responsabilidade
Gerenciar câmeras por cidade com tipos e status diferentes.

## 🏗️ Arquitetura DDD

### Domain Layer
```python
# entities.py
class Camera:
    id: UUID
    city_id: UUID
    name: str
    camera_type: CameraType
    url: str  # RTSP ou RTMP
    status: CameraStatus
    lpr_enabled: bool
    location: Optional[str]
    created_at: datetime
    updated_at: datetime

# value_objects.py
class CameraType(Enum):
    RTSP = "rtsp"  # Alta definição, LPR ativo
    RTMP = "rtmp"  # Padrão, só gravação

class CameraStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PROVISIONING = "provisioning"

# interfaces.py
class ICameraRepository(ABC):
    @abstractmethod
    def create(self, camera: Camera) -> Camera:
        pass
    
    @abstractmethod
    def get_by_city(self, city_id: UUID) -> List[Camera]:
        pass
    
    @abstractmethod
    def count_lpr_cameras(self, city_id: UUID) -> int:
        pass
```

### Infrastructure Layer
```python
# models.py (Django)
class CameraModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    city_id = models.UUIDField()  # FK para cities (DB default)
    name = models.CharField(max_length=100)
    camera_type = models.CharField(max_length=10, choices=CameraType.choices)
    url = models.URLField(max_length=500)
    status = models.CharField(max_length=20, choices=CameraStatus.choices)
    lpr_enabled = models.BooleanField(default=False)
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cameras'
        # Armazenado no DB do tenant (cidade_{slug})
```

### Application Layer
```python
# use_cases.py
class CreateCameraUseCase:
    def __init__(
        self, 
        repository: ICameraRepository,
        streaming_service: IStreamingService
    ):
        self.repository = repository
        self.streaming_service = streaming_service
    
    def execute(self, city_id: UUID, name: str, url: str) -> Camera:
        # Validar tipo pela URL
        camera_type = self._detect_type(url)
        
        # Validar limites
        if camera_type == CameraType.RTSP:
            lpr_count = self.repository.count_lpr_cameras(city_id)
            if lpr_count >= 20:
                raise MaxLPRCamerasExceeded()
        
        # Criar câmera
        camera = Camera(
            city_id=city_id,
            name=name,
            camera_type=camera_type,
            url=url,
            status=CameraStatus.PROVISIONING,
            lpr_enabled=(camera_type == CameraType.RTSP)
        )
        
        # Provisionar no MediaMTX
        self.streaming_service.provision_camera(camera)
        
        camera.status = CameraStatus.ACTIVE
        return self.repository.create(camera)
```

## 📊 Tipos de Câmeras

### RTSP (LPR)
- **Protocolo**: `rtsp://`
- **Quantidade**: Max 20 por cidade
- **IA**: ✅ Ativa (YOLO + OCR)
- **Gravação**: ✅ Contínua
- **Uso**: Detecção de placas

### RTMP (Bullets)
- **Protocolo**: `rtmp://`
- **Quantidade**: Max 1000 por cidade
- **IA**: ❌ Desativada
- **Gravação**: ✅ Contínua
- **Uso**: Monitoramento geral

## ✅ Regras de Negócio

1. **Max 20 RTSP**: Limite de câmeras com LPR por cidade
2. **Max 1000 total**: Limite total de câmeras
3. **Auto-detect tipo**: Detecta RTSP/RTMP pela URL
4. **LPR automático**: RTSP = LPR ativo, RTMP = desativado
5. **Provisioning**: Registra no MediaMTX antes de ativar

## 🚀 Endpoints

```
POST   /api/cameras/              # Criar câmera
GET    /api/cameras/              # Listar câmeras
GET    /api/cameras/{id}/         # Detalhes câmera
PATCH  /api/cameras/{id}/         # Atualizar câmera
DELETE /api/cameras/{id}/         # Deletar câmera
GET    /api/cameras/{id}/stream/  # URL do stream HLS
```

## 📝 Exemplo de Uso

### Criar Câmera RTSP (LPR)
```python
POST /api/cameras/
{
    "name": "Entrada Principal",
    "url": "rtsp://admin:pass@192.168.1.100:554/stream",
    "location": "Portaria"
}

# Response
{
    "id": "uuid",
    "name": "Entrada Principal",
    "camera_type": "rtsp",
    "url": "rtsp://admin:pass@192.168.1.100:554/stream",
    "status": "active",
    "lpr_enabled": true,
    "stream_url": "http://localhost:8888/hls/cam_1/index.m3u8"
}
```

### Criar Câmera RTMP (Gravação)
```python
POST /api/cameras/
{
    "name": "Estacionamento",
    "url": "rtmp://192.168.1.101:1935/live/cam2"
}

# Response
{
    "id": "uuid",
    "name": "Estacionamento",
    "camera_type": "rtmp",
    "url": "rtmp://192.168.1.101:1935/live/cam2",
    "status": "active",
    "lpr_enabled": false,
    "stream_url": "http://localhost:8888/hls/cam_2/index.m3u8"
}
```

## 🔗 Integração

### LPR Mercosul
```python
# Busca apenas câmeras RTSP ativas
GET /api/cameras/?protocol=rtsp&is_active=true

# LPR processa e envia detecções
POST /api/detections/
{
    "camera_id": "uuid",
    "plate": "ABC1D23",
    "confidence": 0.87,
    "image": "base64..."
}
```

### Streaming Service
```python
# Provisiona câmera no MediaMTX
POST /streaming/cameras/provision
{
    "camera_id": "uuid",
    "url": "rtsp://...",
    "path": "cam_1"
}
```

### Frontend
- Grid de câmeras com preview
- Filtros: tipo, status, LPR
- Player HLS integrado
- Indicador de status em tempo real

## 📸 Detections Page

### Exibir Detecções LPR
```
/detections
├── Lista de detecções
│   ├── Placa (texto)
│   ├── Imagem do veículo (.jpeg)
│   ├── Imagem da placa (.jpeg)
│   ├── Câmera
│   ├── Data/Hora
│   └── Confiança
└── Filtros
    ├── Por câmera
    ├── Por data
    └── Por placa
```

### Formato JSON
```json
{
    "id": "uuid",
    "camera_id": "uuid",
    "camera_name": "Entrada Principal",
    "plate": "ABC1D23",
    "confidence": 0.87,
    "vehicle_image": "/media/detections/uuid_vehicle.jpg",
    "plate_image": "/media/detections/uuid_plate.jpg",
    "timestamp": "2026-01-15T00:41:00Z"
}
```

## 🎨 UI Components

### Camera Card
- Thumbnail (screenshot ou placeholder)
- Nome e localização
- Status badge (ativo/erro/inativo)
- LPR badge (se habilitado)
- Tipo (RTSP/RTMP)

### Detection Card
- Placa em destaque
- Imagem do veículo
- Imagem da placa (zoom)
- Câmera origem
- Timestamp
- Confiança (%)
