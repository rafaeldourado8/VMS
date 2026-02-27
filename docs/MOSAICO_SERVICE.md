# Serviço de Mosaicos - VMS

Sistema de visualização simultânea de múltiplas câmeras em mosaico.

## Arquitetura

```
Frontend → HAProxy → Kong → Mosaico Service (FastAPI) → PostgreSQL
                                    ↓
                              MediaMTX (HLS streams)
```

## Características

✅ **Microserviço independente** (FastAPI)  
✅ **Até 10 câmeras por mosaico**  
✅ **Qualidade adaptativa** (ABR automático)  
✅ **Lazy loading** (streams só carregam quando mosaico é aberto)  
✅ **3 modos de qualidade**: Auto, Alta (1080p), Balanceada (720p)  
✅ **Não afeta gravações ou streaming ao vivo**  

## Endpoints

### Listar Mosaicos
```http
GET /mosaico/mosaicos?owner_id=1
Authorization: Bearer {token}
```

### Criar Mosaico
```http
POST /mosaico/mosaicos?owner_id=1
Content-Type: application/json

{
  "name": "Área Externa",
  "layout": "grid_10",
  "cameras": [
    {"camera_id": 1, "position": 1},
    {"camera_id": 2, "position": 2}
  ]
}
```

### Atualizar Câmeras
```http
PUT /mosaico/mosaicos/1/cameras?owner_id=1
Content-Type: application/json

[
  {"camera_id": 3, "position": 1},
  {"camera_id": 4, "position": 2}
]
```

### Deletar Mosaico
```http
DELETE /mosaico/mosaicos/1?owner_id=1
```

## Layouts Disponíveis

- `grid_4`: 2x2 (4 câmeras)
- `grid_9`: 3x3 (9 câmeras)
- `grid_10`: 2x5 (10 câmeras) - **Padrão**

## Qualidade de Streaming

### Modo Auto (ABR)
- Primeiras 4 câmeras: 1080p
- Restantes: 720p
- Adapta automaticamente à banda

### Modo Alta
- Todas as câmeras: 1080p @ 25fps
- Banda necessária: ~20 Mbps

### Modo Balanceada
- Todas as câmeras: 720p @ 25fps
- Banda necessária: ~10 Mbps

## Estimativa de Banda

| Mosaico | Qualidade | Bitrate/cam | Total |
|---------|-----------|-------------|-------|
| 4 câmeras | 1080p | 2 Mbps | 8 Mbps |
| 10 câmeras | 720p | 1 Mbps | 10 Mbps |
| 10 câmeras | 1080p | 2 Mbps | 20 Mbps |

## Deploy

### Iniciar Serviço
```bash
# Windows
scripts\deploy_mosaico.bat

# Linux/Mac
docker-compose up -d mosaico
```

### Verificar Status
```bash
# Health check
curl http://localhost:8007/health

# Logs
docker logs gtvision_mosaico -f
```

### Rebuild
```bash
docker-compose build mosaico
docker-compose up -d mosaico
```

## Banco de Dados

O serviço cria automaticamente as tabelas:

- `mosaicos_mosaico`: Dados do mosaico
- `mosaicos_camera`: Posições das câmeras

## Troubleshooting

### Mosaico não carrega
1. Verificar se serviço está rodando: `docker ps | grep mosaico`
2. Verificar logs: `docker logs gtvision_mosaico`
3. Testar health: `curl http://localhost:8007/health`

### Streams não aparecem
1. Verificar se câmeras estão provisionadas no MediaMTX
2. Verificar se HLS está acessível: `curl http://localhost/hls/cam_1/index.m3u8`
3. Verificar logs do navegador (F12)

### Qualidade ruim
1. Trocar para modo "Alta" no seletor
2. Verificar banda disponível
3. Reduzir número de câmeras no mosaico

## Performance

**Recursos do Serviço:**
- CPU: 0.5 core
- RAM: 512 MB
- Latência: <100ms

**Cliente (10 câmeras 1080p):**
- CPU: ~20-30%
- RAM: ~300-400 MB
- Banda: 20 Mbps

## Segurança

✅ Autenticação via JWT (Kong)  
✅ Isolamento por tenant (owner_id)  
✅ Rate limiting (500 req/min)  
✅ CORS configurado  

## Roadmap

- [ ] Suporte a 16 câmeras (4x4)
- [ ] Layouts personalizados
- [ ] Gravação de mosaico
- [ ] Compartilhamento de mosaico
- [ ] Mosaico em tela dividida
