# 🎥 TESTE DE CÂMERAS REAIS - VMS

## ✅ Correções Aplicadas

O sistema agora está configurado corretamente para provisionar câmeras no MediaMTX:

- ✅ **MediaMTXClient** usando endpoints corretos da API v3
- ✅ **POST** `/v3/config/paths/add/{name}` para adicionar
- ✅ **DELETE** `/v3/config/paths/delete/{name}` para remover
- ✅ **GET** `/v3/config/paths/get/{name}` para status
- ✅ Autenticação configurada
- ✅ Logs detalhados

## 📋 Câmeras para Teste

### Intelbras (RTSP)
```
rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1&subtype=0
rtsp://admin:Camerite123@45.236.226.75:6052/cam/realmonitor?channel=1&subtype=0
rtsp://admin:Camerite123@45.236.226.74:6050/cam/realmonitor?channel=1&subtype=0
rtsp://admin:Camerite123@45.236.226.72:6049/cam/realmonitor?channel=1&subtype=0
rtsp://admin:Camerite123@45.236.226.72:6048/cam/realmonitor?channel=1&subtype=0
rtsp://admin:Camerite123@45.236.226.71:6047/cam/realmonitor?channel=1&subtype=0
rtsp://admin:Camerite123@45.236.226.71:6046/cam/realmonitor?channel=1&subtype=0
rtsp://admin:Camerite123@45.236.226.70:6045/cam/realmonitor?channel=1&subtype=0
rtsp://admin:Camerite123@45.236.226.70:6044/cam/realmonitor?channel=1&subtype=0
```

### RTMP Intelbras
```
rtmp://inst-iwvio-srs-rtmp-intelbras.camerite.services:1935/record/7KOM27157189T.stream
```

### Hikvision (RTSP)
```
rtsp://admin:Camerite@186.226.193.111:602/h264/ch1/main/av_stream
rtsp://admin:Camerite@186.226.193.111:601/h264/ch1/main/av_stream
rtsp://admin:Camerite@170.84.217.84:603/h264/ch1/main/av_stream
```

### RTMP Hikvision
```
rtmp://inst-czd17-srs-rtmp-hik-pro-connect.camerite.services:1935/record/FC2487833.stream
rtmp://inst-czd17-srs-rtmp-hik-pro-connect.camerite.services:1935/record/FC2487237.stream
```

## 🧪 Como Testar

### Opção 1: Via Frontend (Recomendado)

1. Acesse: **http://localhost**
2. Faça login no sistema
3. Vá em **Câmeras** > **Adicionar Câmera**
4. Preencha:
   - **Nome**: Camera Intelbras 1
   - **URL RTSP**: Cole uma das URLs acima
   - **Localização**: Teste
   - **Ativa**: ✓
5. Clique em **Salvar**
6. Verifique os logs: `docker-compose logs -f streaming`

### Opção 2: Via API Direta (Requer Token)

```bash
# 1. Obter token de autenticação
curl -X POST http://localhost/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"sua_senha"}'

# 2. Criar câmera
curl -X POST http://localhost/api/cameras/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{
    "name": "Camera Teste 1",
    "rtsp_url": "rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1&subtype=0",
    "location": "Teste",
    "is_active": true
  }'
```

### Opção 3: Teste Direto no MediaMTX (Sem Backend)

```bash
# Adicionar path diretamente no MediaMTX
docker-compose exec streaming python -c "
import httpx
response = httpx.post(
    'http://mediamtx:9997/v3/config/paths/add/test_cam_1',
    json={
        'source': 'rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1&subtype=0',
        'sourceOnDemand': True
    },
    auth=('mediamtx_api_user', 'GtV!sionMed1aMTX\$2025')
)
print(f'Status: {response.status_code}')
print(f'Response: {response.text}')
"

# Acessar stream HLS
# http://localhost:8888/test_cam_1/

# Remover path
docker-compose exec streaming python -c "
import httpx
response = httpx.delete(
    'http://mediamtx:9997/v3/config/paths/delete/test_cam_1',
    auth=('mediamtx_api_user', 'GtV!sionMed1aMTX\$2025')
)
print(f'Removido: {response.status_code}')
"
```

## 📊 Verificar Logs

```bash
# Logs do streaming service
docker-compose logs -f streaming

# Logs do MediaMTX
docker-compose logs -f mediamtx

# Logs do backend
docker-compose logs -f backend
```

## ✅ O que Esperar

Ao criar uma câmera, você deve ver nos logs:

```
streaming  | 🎥 Provisionando câmera 33: rtsp://admin:Camerite123@...
streaming  | ✅ Stream criado: cam_33 -> http://mediamtx:8889/cam_33
streaming  | 🔧 Adicionando path no MediaMTX: cam_33
streaming  | ✅ Path cam_33 adicionado com sucesso
streaming  | ✅ Câmera 33 provisionada com sucesso
```

## 🔗 URLs de Acesso

Após criar a câmera com ID `X`, o stream estará disponível em:

- **HLS**: `http://localhost:8888/cam_X/`
- **WebRTC**: `http://localhost:8889/cam_X/`
- **RTSP**: `rtsp://localhost:8554/cam_X`

## 🐛 Troubleshooting

### Erro 404 ao adicionar path
✅ **RESOLVIDO** - Endpoints da API v3 corrigidos

### Erro de autenticação
- Verifique as credenciais no `.env`
- Confirme que `MEDIAMTX_API_USER` e `MEDIAMTX_API_PASS` estão corretos

### Câmera não conecta
- Verifique se a URL RTSP/RTMP está acessível
- Teste com VLC: `vlc rtsp://...`
- Verifique firewall e portas

### Stream não aparece
- Aguarde alguns segundos (on-demand)
- Verifique logs do MediaMTX
- Acesse diretamente: `http://localhost:8888/cam_X/`

## 📝 Notas

- O sistema usa **sourceOnDemand=true** por padrão
- Streams são iniciados apenas quando solicitados
- Suporta RTSP, RTMP, HLS e WebRTC
- Limite de 4 câmeras simultâneas por mosaico (MVP)
