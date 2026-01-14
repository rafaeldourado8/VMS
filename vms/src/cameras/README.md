# 📹 Módulo Cameras - Auto-detecção LPR

## 📋 Responsabilidade

Gerenciar câmeras com **auto-detecção de tipo** pela URL e ativação automática de LPR.

---

## 🎯 Funcionalidades Principais

### Auto-detecção de Tipo
- **RTSP** (`rtsp://...`) → LPR ativo automaticamente (max 20)
- **RTMP** (`rtmp://...`) → Bullet, sem LPR (max 1000)

### Regras de IA
- **RTSP**: IA LPR ativa em tempo real
- **RTMP**: Apenas Sentinela (busca retroativa em gravações)

---

## 🏗️ Arquitetura

```
Domain (Python puro)
  ↓
Application (Use Cases)
  ↓
Infrastructure (Django)
```

---

## 📦 Estrutura

```
cameras/
├── domain/
│   ├── entities/
│   │   └── camera.py              ✅ Auto-detecção de tipo
│   ├── value_objects/
│   │   ├── camera_type.py         ✅ RTSP/RTMP
│   │   └── camera_status.py       ✅ Active/Inactive/Error
│   ├── repositories/
│   │   └── camera_repository.py   ✅ Interface
│   └── events/
│       ├── camera_created.py      ✅
│       └── camera_activated.py    ✅
│
├── application/
│   └── use_cases/
│       ├── create_camera.py       ✅ Criar com auto-detecção
│       ├── activate_camera.py     ✅ Ativar câmera
│       └── list_cameras.py        ✅ Listar câmeras
│
├── infrastructure/
│   └── django/
│       ├── models.py              ✅ CameraModel + lpr_enabled
│       ├── repository.py          ✅ Implementação
│       └── admin.py               ✅ Django Admin + status LPR
│
└── tests/
    └── unit/
        ├── test_camera_entity.py          ✅ 6 tests
        └── test_create_camera_use_case.py ✅ 4 tests
```

---

## 🎯 Domain

### Camera Entity (com auto-detecção)

```python
@dataclass
class Camera:
    id: str
    name: str
    stream_url: str  # rtsp:// ou rtmp://
    city_id: str
    type: str = None  # Auto-detectado
    lpr_enabled: bool = False  # Auto-ativado se RTSP
    
    def __post_init__(self):
        if self.type is None:
            self.type = self._detect_type()
        self.lpr_enabled = self.type == 'rtsp'
    
    def _detect_type(self) -> str:
        if self.stream_url.startswith('rtsp://'):
            return 'rtsp'
        elif self.stream_url.startswith('rtmp://'):
            return 'rtmp'
        raise ValueError(f"Invalid stream URL")
```

### Exemplo de Uso

```python
# Criar câmera LPR (RTSP)
camera_lpr = Camera(
    id='1',
    name='Camera LPR 1',
    stream_url='rtsp://192.168.1.100/stream',
    city_id='city-1'
)
# Resultado:
# - type = 'rtsp' (auto-detectado)
# - lpr_enabled = True (auto-ativado)

# Criar câmera Bullet (RTMP)
camera_bullet = Camera(
    id='2',
    name='Camera Bullet 1',
    stream_url='rtmp://192.168.1.101/stream',
    city_id='city-1'
)
# Resultado:
# - type = 'rtmp' (auto-detectado)
# - lpr_enabled = False
```

---

## 🤖 Regras de IA

### RTSP (LPR)
- ✅ **IA em tempo real**: YOLO + OCR
- ✅ **Detecção de placas**: Automática
- ✅ **Alertas**: Blacklist em tempo real
- ✅ **Sentinela**: Busca retroativa disponível
- ⚠️ **Limite**: Max 20 por cidade

### RTMP (Bullet)
- ❌ **IA em tempo real**: Desativada
- ❌ **Detecção de placas**: Não disponível
- ✅ **Gravação**: 24/7
- ✅ **Sentinela**: Busca retroativa disponível
- ✅ **Limite**: Max 1000 por cidade

---

## 📊 Testes e Qualidade

### Testes Unitários
```
✅ 10 passed in 0.34s
✅ 95% de cobertura
```

### Complexidade Ciclomática
```
✅ Média: A (1.55)
✅ 31 blocos analisados
```

### Detalhamento

| Componente | Complexidade | Status |
|------------|--------------|--------|
| Camera entity | A (2) | ✅ |
| _detect_type | A (3) | ✅ |
| CreateCameraUseCase | A (4) | ✅ |
| ActivateCameraUseCase | A (3) | ✅ |

---

## ✅ Implementado

### Domain
- [x] Camera entity com auto-detecção
- [x] Validação de URL (rtsp:// ou rtmp://)
- [x] Auto-ativação de LPR para RTSP
- [x] CameraType VO
- [x] CameraStatus VO
- [x] ICameraRepository
- [x] Events

### Application
- [x] CreateCameraUseCase (auto-detecção)
- [x] Validação de limites (1000 total, 20 LPR)
- [x] ActivateCameraUseCase
- [x] ListCamerasUseCase

### Infrastructure
- [x] CameraModel com lpr_enabled
- [x] DjangoCameraRepository
- [x] CameraAdmin com status LPR visual

### Tests
- [x] 10 testes unitários
- [x] 95% cobertura
- [x] Teste de auto-detecção
- [x] Teste de validação de URL

---

## 🎨 Django Admin

### Visualização
- Nome da câmera
- Tipo (RTSP/RTMP)
- **Status LPR**: ✅ LPR Ativo / ❌ Sem LPR
- Status (Active/Inactive/Error)
- Cidade
- Data de criação

### Ações em Lote
- Ativar câmeras selecionadas
- Desativar câmeras selecionadas

### Campos Read-only
- ID
- Tipo (auto-detectado)
- LPR Enabled (auto-ativado)
- Datas

---

## 🚀 Próximo

- [ ] Migrations
- [ ] Seeds (câmeras de teste)
- [ ] Integração com módulo Streaming
- [ ] Integração com módulo LPR
