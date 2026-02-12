# CONFIGURAÇÃO PARA MÁQUINA DE IA

## PROBLEMA: Máquina de IA busca 192.168.0.102 mas este PC está em 192.168.0.103

## SOLUÇÃO 1 (RECOMENDADO): Atualizar IP na máquina de IA
Altere de 192.168.0.102 para 192.168.0.103

## SOLUÇÃO 2: Fixar IP deste PC para 192.168.0.102
Execute como Administrador: `fixar_ip_102.bat`

## URLs RTSP para usar na máquina de IA:

```
rtsp://192.168.0.103:8554/NOME_DA_CAMERA
```

### Exemplos:
```python
# Câmera 1
rtsp://192.168.0.103:8554/cam_1

# Câmera 2
rtsp://192.168.0.103:8554/cam_2

# Câmera com LPR
rtsp://192.168.0.103:8554/cam_1_ai
```

## Código Python para a máquina de IA:

```python
import cv2

# Configuração
MEDIAMTX_HOST = "192.168.0.103"
CAMERA_NAME = "cam_1"  # Altere conforme necessário

# URL RTSP
rtsp_url = f"rtsp://{MEDIAMTX_HOST}:8554/{CAMERA_NAME}"

# Conectar ao stream
cap = cv2.VideoCapture(rtsp_url)

if cap.isOpened():
    print(f"✓ Conectado: {rtsp_url}")
    ret, frame = cap.read()
    if ret:
        print(f"✓ Frame recebido: {frame.shape}")
        # Processar frame com IA aqui
else:
    print(f"✗ Falha ao conectar: {rtsp_url}")

cap.release()
```

## Teste rápido na máquina de IA:

```bash
# Com ffmpeg
ffmpeg -i rtsp://192.168.0.103:8554/cam_1 -frames:v 1 test.jpg

# Com VLC
vlc rtsp://192.168.0.103:8554/cam_1
```

## Se não funcionar:

### 1. Libere o firewall do Windows (nesta máquina):

Execute como Administrador:
```powershell
New-NetFirewallRule -DisplayName "MediaMTX RTSP" -Direction Inbound -Protocol TCP -LocalPort 8554 -Action Allow
New-NetFirewallRule -DisplayName "MediaMTX API" -Direction Inbound -Protocol TCP -LocalPort 9997 -Action Allow
```

### 2. Verifique se as máquinas estão na mesma rede:

Na máquina de IA, teste o ping:
```bash
ping 192.168.0.103
```

### 3. Reinicie o MediaMTX:

```cmd
docker-compose restart mediamtx
```

## Listar câmeras disponíveis:

```bash
curl http://192.168.0.103:9997/v3/paths/list
```
