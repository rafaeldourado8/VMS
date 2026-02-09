# 🚀 ARQUITETURA ELÁSTICA - MediaMTX Auto-Scaling

## Conceito

Criar instâncias MediaMTX **sob demanda** baseado em carga:
- 1 instância: 0-25 câmeras
- 2 instâncias: 26-50 câmeras  
- 3 instâncias: 51-75 câmeras
- N instâncias: auto-scaling

---

## Implementação

### 1. MediaMTX Manager Service

```python
class MediaMTXManager:
    """Gerencia instâncias MediaMTX dinamicamente."""
    
    MAX_CAMERAS_PER_INSTANCE = 25
    
    def __init__(self):
        self.instances = []  # Lista de instâncias ativas
        self.camera_map = {}  # {camera_id: instance_id}
    
    async def get_or_create_instance(self, camera_id: int):
        """Retorna instância disponível ou cria nova."""
        
        # Verificar instâncias existentes
        for instance in self.instances:
            if instance.camera_count < self.MAX_CAMERAS_PER_INSTANCE:
                return instance
        
        # Criar nova instância
        instance_id = len(self.instances) + 1
        new_instance = await self.create_instance(instance_id)
        self.instances.append(new_instance)
        
        return new_instance
    
    async def create_instance(self, instance_id: int):
        """Cria nova instância MediaMTX via Docker API."""
        
        import docker
        client = docker.from_env()
        
        container = client.containers.run(
            image="bluenviron/mediamtx:latest-ffmpeg",
            name=f"mediamtx_{instance_id}",
            detach=True,
            ports={
                '8888/tcp': 8888 + instance_id,  # HLS
                '9997/tcp': 9997 + instance_id,  # API
            },
            volumes={
                f'mediamtx_recordings_{instance_id}': {
                    'bind': '/recordings',
                    'mode': 'rw'
                }
            },
            environment={
                'TZ': 'America/Sao_Paulo'
            },
            restart_policy={"Name": "unless-stopped"}
        )
        
        return MediaMTXInstance(
            id=instance_id,
            container=container,
            api_url=f"http://localhost:{9997 + instance_id}",
            hls_url=f"http://localhost:{8888 + instance_id}"
        )
    
    async def scale_down(self):
        """Remove instâncias ociosas."""
        for instance in self.instances:
            if instance.camera_count == 0:
                await instance.stop()
                self.instances.remove(instance)
```

---

## Vantagens

✅ **Elástico**: Cria instâncias apenas quando necessário  
✅ **Econômico**: Remove instâncias ociosas  
✅ **Simples**: Sem configuração manual  
✅ **Escalável**: Suporta 100+ câmeras automaticamente

---

## Desvantagens

❌ **Complexo**: Requer Docker API  
❌ **Latência**: ~10s para criar nova instância  
❌ **Overhead**: Gerenciamento de múltiplos containers

---

## Alternativa Simples: Pool Fixo

Criar **3 instâncias fixas** desde o início:

```yaml
services:
  mediamtx_1:
    ports: ["8888:8888", "9997:9997"]
  
  mediamtx_2:
    ports: ["8889:8888", "9998:9997"]
  
  mediamtx_3:
    ports: ["8890:8888", "9999:9997"]
```

**Roteamento Round-Robin:**
- cam_1, cam_4, cam_7 → mediamtx_1
- cam_2, cam_5, cam_8 → mediamtx_2  
- cam_3, cam_6, cam_9 → mediamtx_3

---

## Recomendação

Para **11 câmeras atuais**: 
- ✅ **1 instância** é suficiente
- ⏳ Implementar auto-scaling quando atingir **20+ câmeras**

Para **50+ câmeras futuras**:
- ✅ **Pool fixo de 3 instâncias** (mais simples)
- ⏳ Auto-scaling apenas se passar de 75 câmeras
