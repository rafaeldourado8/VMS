# CONFIGURAÇÃO DE ACESSO EXTERNO AO MEDIAMTX

## Problema Resolvido
O MediaMTX não estava expondo a API RTSP para consumo externo pela máquina de IA.

## Mudanças Realizadas

### 1. mediamtx.yml
- **API Address**: Alterado de `:9997` para `0.0.0.0:9997` (aceita conexões de qualquer IP)
- **RTSP Address**: Alterado de `:8554` para `0.0.0.0:8554` (aceita conexões de qualquer IP)
- **Autenticação**: Removida restrição de IP para acesso à API (permite qualquer IP)

### 2. Portas Expostas (docker-compose.yml)
Já estavam corretas:
- `8554:8554` - RTSP
- `8888:8888` - HLS
- `8889:8889` - WebRTC
- `9996:9996` - Playback
- `9997:9997` - API

## Configuração na Máquina de IA

### 1. Obter o IP desta máquina
Execute no Windows:
```cmd
ipconfig
```
Anote o IPv4 da sua rede (ex: 192.168.1.100)

### 2. Configurar URL RTSP na máquina de IA
Use o formato:
```
rtsp://IP_DESTA_MAQUINA:8554/NOME_DA_CAMERA
```

Exemplo:
```python
# Na máquina de IA
input_stream = "rtsp://192.168.1.100:8554/cam_1"
```

### 3. Testar Conectividade
Na máquina de IA, teste com ffmpeg ou VLC:
```bash
# Com ffmpeg
ffmpeg -i rtsp://192.168.1.100:8554/cam_1 -frames:v 1 test.jpg

# Com VLC
vlc rtsp://192.168.1.100:8554/cam_1
```

## Firewall do Windows

Se ainda não funcionar, libere as portas no firewall:

### Via PowerShell (Execute como Administrador):
```powershell
# RTSP
New-NetFirewallRule -DisplayName "MediaMTX RTSP" -Direction Inbound -Protocol TCP -LocalPort 8554 -Action Allow

# API
New-NetFirewallRule -DisplayName "MediaMTX API" -Direction Inbound -Protocol TCP -LocalPort 9997 -Action Allow

# HLS
New-NetFirewallRule -DisplayName "MediaMTX HLS" -Direction Inbound -Protocol TCP -LocalPort 8888 -Action Allow
```

### Via Interface Gráfica:
1. Abra "Firewall do Windows com Segurança Avançada"
2. Clique em "Regras de Entrada"
3. Clique em "Nova Regra..."
4. Selecione "Porta" → Avançar
5. TCP → Portas locais específicas: `8554, 9997, 8888`
6. Permitir a conexão → Avançar
7. Marque todos os perfis → Avançar
8. Nome: "MediaMTX Ports" → Concluir

## Reiniciar MediaMTX

Após as mudanças, reinicie o container:
```cmd
docker-compose restart mediamtx
```

## Verificar Status

Execute o script de teste:
```cmd
test_external_rtsp.bat
```

Ou manualmente:
```cmd
# Ver se as portas estão escutando
netstat -an | findstr ":8554"
netstat -an | findstr ":9997"

# Testar API
curl http://localhost:9997/v3/config/global/get
```

## Exemplo de Código Python na Máquina de IA

```python
import cv2

# Substitua pelo IP real desta máquina
MEDIAMTX_HOST = "192.168.1.100"
CAMERA_NAME = "cam_1"

rtsp_url = f"rtsp://{MEDIAMTX_HOST}:8554/{CAMERA_NAME}"

cap = cv2.VideoCapture(rtsp_url)
if cap.isOpened():
    print(f"✓ Conectado ao stream: {rtsp_url}")
    ret, frame = cap.read()
    if ret:
        print(f"✓ Frame recebido: {frame.shape}")
else:
    print(f"✗ Falha ao conectar: {rtsp_url}")

cap.release()
```

## Troubleshooting

### Erro: "Connection refused"
- Verifique se o MediaMTX está rodando: `docker ps | findstr mediamtx`
- Verifique se as portas estão expostas: `netstat -an | findstr ":8554"`
- Verifique o firewall do Windows

### Erro: "Connection timeout"
- Verifique se a máquina de IA consegue pingar este PC
- Verifique se ambas as máquinas estão na mesma rede
- Verifique configurações de rede/roteador

### Stream não encontrado (404)
- Verifique se a câmera está publicando no MediaMTX
- Liste os streams ativos: `curl http://localhost:9997/v3/paths/list`
- Verifique o nome correto da câmera

## Segurança

Para produção, considere:
1. Adicionar autenticação RTSP no mediamtx.yml
2. Usar VPN entre as máquinas
3. Restringir IPs permitidos na configuração
4. Usar RTSPS (RTSP sobre TLS)
