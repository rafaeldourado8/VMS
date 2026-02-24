# Correção: Clips Corrompidos e Erro 401

## Problemas

### 1. Clips Corrompidos

Os clips criados estavam sendo corrompidos durante o processo de corte e concatenação. O vídeo era gerado, mas não podia ser reproduzido corretamente.

### 2. Erro 401 (Unauthorized)

Ao tentar reproduzir clips na interface, o navegador retornava erro 401 porque o endpoint de vídeo exigia autenticação.

## Causa Raiz

### 1. Clips Corrompidos

O serviço de clips estava usando `-c copy` (stream copy) no FFmpeg, que copia os streams de vídeo e áudio sem re-encodar. Isso causava problemas quando:

1. **Múltiplos segmentos com parâmetros diferentes**: Segmentos MP4 de 60s podem ter codecs ou parâmetros ligeiramente diferentes
2. **Keyframes desalinhados**: A concatenação sem re-encode pode resultar em keyframes mal posicionados
3. **Timestamps inconsistentes**: Problemas de sincronização entre áudio e vídeo ao concatenar

### 2. Erro 401

O endpoint `/api/clips/{id}/video/` estava usando a permissão padrão `IsAuthenticated` da classe `ClipViewSet`, impedindo que o player HTML5 acessasse o vídeo sem token de autenticação.

## Solução Implementada

### 1. Re-encode com libx264 (services/clips/main.py)

Substituímos `-c copy` por re-encode explícito:

```python
# ANTES (corrompido)
cmd = [
    "ffmpeg", "-y",
    "-ss", str(offset),
    "-i", str(input_file),
    "-t", str(duration),
    "-c", "copy",  # ❌ Stream copy
    "-movflags", "+faststart",
    str(output_file)
]

# DEPOIS (corrigido)
cmd = [
    "ffmpeg", "-y",
    "-ss", str(offset),
    "-i", str(input_file),
    "-t", str(duration),
    "-c:v", "libx264",           # ✅ Re-encode vídeo
    "-preset", "fast",            # ✅ Velocidade razoável
    "-crf", "23",                 # ✅ Qualidade boa
    "-c:a", "aac",                # ✅ Re-encode áudio
    "-b:a", "128k",               # ✅ Bitrate áudio
    "-movflags", "+faststart",    # ✅ Streaming web
    "-avoid_negative_ts", "make_zero",  # ✅ Corrige timestamps
    "-fflags", "+genpts",         # ✅ Gera timestamps
    str(output_file)
]
```

### 2. Acesso público ao vídeo (backend/apps/clips/views.py)

Adicionamos `AllowAny` ao endpoint de vídeo:

```python
# ANTES (401 Unauthorized)
@action(detail=True, methods=['get'])
def video(self, request, pk=None):
    clip = self.get_object()  # Requer autenticação
    ...

# DEPOIS (acesso público)
@action(detail=True, methods=['get'], permission_classes=[AllowAny])
def video(self, request, pk=None):
    clip = get_object_or_404(Clip, pk=pk)  # Sem verificação de owner
    ...
```

### 2. Parâmetros Adicionados

- **`-c:v libx264`**: Re-encode vídeo com H.264 (compatibilidade universal)
- **`-preset fast`**: Balanço entre velocidade e qualidade
- **`-crf 23`**: Qualidade visual boa (18-28, onde 23 é padrão)
- **`-c:a aac`**: Re-encode áudio com AAC (compatibilidade universal)
- **`-b:a 128k`**: Bitrate de áudio adequado
- **`-avoid_negative_ts make_zero`**: Corrige timestamps negativos
- **`-fflags +genpts`**: Gera timestamps de apresentação

### 3. Aplicado em Ambos os Casos

A correção foi aplicada tanto para:
- **Clip de arquivo único**: Corte direto de um segmento
- **Clip de múltiplos arquivos**: Concatenação + corte

## Trade-offs

### Vantagens
✅ Clips sempre reproduzíveis e não corrompidos  
✅ Compatibilidade universal (web, mobile, desktop)  
✅ Timestamps corretos e sincronização A/V perfeita  
✅ Qualidade visual mantida (CRF 23)

### Desvantagens
⚠️ Processamento mais lento (re-encode vs copy)  
⚠️ Uso de CPU durante criação do clip  
⚠️ Arquivo final pode ser ligeiramente maior

## Impacto de Performance

- **Antes**: ~1-2s para clip de 30s (stream copy)
- **Depois**: ~5-10s para clip de 30s (re-encode)

Para clips de até 5 minutos (limite atual), o tempo de processamento é aceitável.

## Como Testar

Execute o script de teste:

```bash
# Windows
python scripts\test_clip_creation.py

# Linux/Mac
python3 scripts/test_clip_creation.py
```

O script irá:
1. Criar um clip de teste de 30s
2. Aguardar processamento
3. Baixar o clip
4. Verificar integridade com FFprobe
5. Reportar sucesso ou falha

## Aplicar a Correção

### 1. Reconstruir containers

```bash
# Clips service (corrupção)
docker-compose build clips
docker-compose up -d clips

# Backend (erro 401)
docker-compose restart backend
```

### 2. Verificar logs

```bash
# Clips service
docker-compose logs -f clips

# Backend
docker-compose logs -f backend
```

### 3. Testar acesso ao vídeo

```bash
# Deve retornar 404 (clip não existe) ou 200 (OK), não 401
scripts\test_clip_access.bat
```

### 3. Testar criação de clip

Use a interface web ou o script de teste para criar um clip e verificar se reproduz corretamente.

## Monitoramento

Verifique os logs do serviço de clips para erros do FFmpeg:

```bash
docker-compose logs clips | grep -i "error\|failed"
```

## Próximos Passos (Opcional)

Se o tempo de processamento for um problema:

1. **Usar GPU**: `-c:v h264_nvenc` (requer NVIDIA GPU)
2. **Preset mais rápido**: `-preset ultrafast` (menor qualidade)
3. **Processamento assíncrono**: Notificar usuário quando pronto
4. **Cache de clips**: Reutilizar clips já criados

## Referências

- [FFmpeg H.264 Encoding Guide](https://trac.ffmpeg.org/wiki/Encode/H.264)
- [FFmpeg Concatenation](https://trac.ffmpeg.org/wiki/Concatenate)
- [Fixing Corrupted MP4](https://superuser.com/questions/1251776/how-to-fix-corrupted-mp4-video-file)
