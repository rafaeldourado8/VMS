# 🎯 Sprint 7: Deploy + Monitoring (7 dias)

## 📋 Objetivo

Deploy em produção com Docker Compose e monitoring completo.

---

## 🚀 Entregáveis

### Dia 1-2: Docker Compose Produção

#### Entities
```python
# sentinela/domain/entities/vehicle_search.py
@dataclass
class VehicleSearch:
    id: str
    city_id: str
    user_id: str
    plate: str | None
    color: str | None
    vehicle_type: str | None
    start_date: datetime
    end_date: datetime
    status: str = 'pending'  # pending, processing, completed, failed
    created_at: datetime = None
```

```python
# sentinela/domain/entities/trajectory.py
@dataclass
class Trajectory:
    search_id: str
    points: list[TrajectoryPoint]
    
    def get_timeline(self) -> list[TrajectoryPoint]:
        return sorted(self.points, key=lambda x: x.timestamp)
    
    def get_cameras_visited(self) -> list[str]:
        return list(set(p.camera_id for p in self.points))
```

```python
# sentinela/domain/entities/trajectory_point.py
@dataclass
class TrajectoryPoint:
    camera_id: str
    camera_name: str
    timestamp: datetime
    image_url: str
    confidence: float
    location: str | None = None
```

#### Use Cases
```python
# sentinela/application/use_cases/search_vehicle.py
class SearchVehicleUseCase:
    def __init__(
        self,
        search_repo: IVehicleSearchRepository,
        recording_repo: IRecordingRepository,
        rekognition_provider: IRekognitionProvider
    ):
        self._search_repo = search_repo
        self._recording_repo = recording_repo
        self._rekognition = rekognition_provider
    
    async def execute(self, request: SearchVehicleRequest) -> str:
        # Cria busca
        search = VehicleSearch(
            id=str(uuid4()),
            city_id=request.city_id,
            user_id=request.user_id,
            plate=request.plate,
            color=request.color,
            vehicle_type=request.vehicle_type,
            start_date=request.start_date,
            end_date=request.end_date,
            created_at=datetime.now()
        )
        
        await self._search_repo.save(search)
        
        # Processa assíncrono
        asyncio.create_task(self._process_search(search.id))
        
        return search.id
    
    async def _process_search(self, search_id: str):
        search = await self._search_repo.find_by_id(search_id)
        search.status = 'processing'
        await self._search_repo.save(search)
        
        try:
            # Lista gravações no período
            recordings = await self._recording_repo.list_by_date_range(
                search.city_id,
                search.start_date,
                search.end_date
            )
            
            trajectory_points = []
            
            # Processa cada gravação
            for recording in recordings:
                results = await self._rekognition.search_vehicle(
                    video_path=recording.file_path,
                    criteria=SearchCriteria(
                        plate=search.plate,
                        color=search.color,
                        vehicle_type=search.vehicle_type
                    )
                )
                
                for result in results:
                    point = TrajectoryPoint(
                        camera_id=recording.camera_id,
                        camera_name=result.camera_name,
                        timestamp=result.timestamp,
                        image_url=result.image_url,
                        confidence=result.confidence
                    )
                    trajectory_points.append(point)
            
            # Salva trajetória
            trajectory = Trajectory(
                search_id=search.id,
                points=trajectory_points
            )
            await self._trajectory_repo.save(trajectory)
            
            search.status = 'completed'
        except Exception as e:
            search.status = 'failed'
            search.error_message = str(e)
        
        await self._search_repo.save(search)
```

---

### Dia 3-4: Rekognition Integration

#### Rekognition Provider
```python
# sentinela/infrastructure/aws/rekognition_provider.py
import boto3
import cv2

class RekognitionProvider(IRekognitionProvider):
    def __init__(self):
        self.client = boto3.client('rekognition')
    
    async def search_vehicle(
        self,
        video_path: str,
        criteria: SearchCriteria
    ) -> list[SearchResult]:
        # Extrai frames do vídeo
        frames = await self._extract_frames(video_path, fps=1)
        
        results = []
        for frame_data in frames:
            # Detecta objetos
            response = self.client.detect_labels(
                Image={'Bytes': frame_data['bytes']},
                MaxLabels=10,
                MinConfidence=75
            )
            
            # Filtra por critérios
            if self._matches_criteria(response, criteria):
                results.append(SearchResult(
                    timestamp=frame_data['timestamp'],
                    image_url=await self._save_frame(frame_data),
                    confidence=response['Labels'][0]['Confidence'] / 100,
                    camera_name=frame_data['camera_name']
                ))
        
        return results
    
    def _matches_criteria(self, response, criteria) -> bool:
        labels = {l['Name'].lower() for l in response['Labels']}
        
        # Verifica tipo de veículo
        if criteria.vehicle_type:
            if criteria.vehicle_type.lower() not in labels:
                return False
        
        # Verifica cor (se disponível)
        if criteria.color:
            colors = {l['Name'].lower() for l in response['Labels'] 
                     if 'Color' in l.get('Categories', [])}
            if criteria.color.lower() not in colors:
                return False
        
        return True
```

---

### Dia 5: Docker Compose Produção

#### docker-compose.prod.yml
```yaml
version: '3.8'

services:
  # PostgreSQL Admin
  postgres_admin:
    image: postgres:15
    environment:
      POSTGRES_DB: vms_admin
      POSTGRES_USER: vms_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_admin_data:/var/lib/postgresql/data
    networks:
      - vms_network

  # PostgreSQL Cidades (exemplo)
  postgres_cidade_sp:
    image: postgres:15
    environment:
      POSTGRES_DB: cidade_sp
      POSTGRES_USER: vms_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_sp_data:/var/lib/postgresql/data
    networks:
      - vms_network

  # Redis
  redis:
    image: redis:7-alpine
    networks:
      - vms_network

  # RabbitMQ
  rabbitmq:
    image: rabbitmq:3.13-management
    environment:
      RABBITMQ_DEFAULT_USER: vms
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD}
    networks:
      - vms_network

  # MediaMTX
  mediamtx:
    image: bluenviron/mediamtx:latest
    ports:
      - "8554:8554"  # RTSP
      - "8888:8888"  # HLS
      - "9997:9997"  # API
    volumes:
      - ./mediamtx.yml:/mediamtx.yml
    networks:
      - vms_network

  # Backend (Django + FastAPI)
  backend:
    build: ./src
    command: uvicorn main:app --host 0.0.0.0 --port 8000
    environment:
      DATABASE_URL: postgresql://vms_user:${POSTGRES_PASSWORD}@postgres_admin/vms_admin
      REDIS_URL: redis://redis:6379/0
      CELERY_BROKER_URL: amqp://vms:${RABBITMQ_PASSWORD}@rabbitmq:5672/
      MEDIAMTX_BASE_URL: http://mediamtx:9997
    depends_on:
      - postgres_admin
      - redis
      - rabbitmq
      - mediamtx
    networks:
      - vms_network

  # Celery Worker
  celery_worker:
    build: ./src
    command: celery -A config worker -l info -c 4
    environment:
      DATABASE_URL: postgresql://vms_user:${POSTGRES_PASSWORD}@postgres_admin/vms_admin
      REDIS_URL: redis://redis:6379/0
      CELERY_BROKER_URL: amqp://vms:${RABBITMQ_PASSWORD}@rabbitmq:5672/
    depends_on:
      - postgres_admin
      - redis
      - rabbitmq
    networks:
      - vms_network

  # Celery Beat
  celery_beat:
    build: ./src
    command: celery -A config beat -l info
    environment:
      DATABASE_URL: postgresql://vms_user:${POSTGRES_PASSWORD}@postgres_admin/vms_admin
      REDIS_URL: redis://redis:6379/0
      CELERY_BROKER_URL: amqp://vms:${RABBITMQ_PASSWORD}@rabbitmq:5672/
    depends_on:
      - postgres_admin
      - redis
      - rabbitmq
    networks:
      - vms_network

  # Prometheus
  prometheus:
    image: prom/prometheus
    volumes:
      - ./config/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - vms_network

  # Grafana
  grafana:
    image: grafana/grafana
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"
    networks:
      - vms_network

volumes:
  postgres_admin_data:
  postgres_sp_data:
  prometheus_data:
  grafana_data:

networks:
  vms_network:
    driver: bridge
```

---

### Dia 6: Monitoring

#### Prometheus Config
```yaml
# config/prometheus/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'vms_backend'
    static_configs:
      - targets: ['backend:8000']
  
  - job_name: 'mediamtx'
    static_configs:
      - targets: ['mediamtx:9998']
  
  - job_name: 'celery'
    static_configs:
      - targets: ['celery_worker:9999']
```

#### Metrics Endpoint
```python
# presentation/fastapi/metrics.py
from prometheus_client import Counter, Histogram, generate_latest

detections_counter = Counter('vms_detections_total', 'Total detections')
detection_latency = Histogram('vms_detection_latency_seconds', 'Detection latency')

@router.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

---

### Dia 7: Deploy + Documentação

#### Deploy Script
```bash
#!/bin/bash
# deploy.sh

# Build images
docker-compose -f docker-compose.prod.yml build

# Run migrations
docker-compose -f docker-compose.prod.yml run backend python manage.py migrate

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check health
docker-compose -f docker-compose.prod.yml ps
```

#### Documentação
- [ ] README de deploy
- [ ] Guia de configuração
- [ ] Troubleshooting
- [ ] Backup e restore

---

## ✅ Checklist

### Sentinela
- [ ] VehicleSearch entity
- [ ] Trajectory entity
- [ ] SearchVehicleUseCase
- [ ] RekognitionProvider
- [ ] Django Admin

### Deploy
- [ ] docker-compose.prod.yml
- [ ] Migrations
- [ ] Seeds
- [ ] Health checks

### Monitoring
- [ ] Prometheus
- [ ] Grafana dashboards
- [ ] Alertas
- [ ] Logs centralizados

---

## 🎯 Métricas de Sucesso

1. ✅ Sentinela funcionando
2. ✅ Deploy em produção
3. ✅ Monitoring ativo
4. ✅ 99% uptime
5. ✅ Documentação completa

---

## 🎉 Projeto Completo!
