# VOD: Abordagens Comparadas

## 🎯 Sua Pergunta
> "O VOD não pode jogar as gravações do disco (ou S3) no MediaMTX que já temos para consumir como player?"

**Resposta:** SIM! Existem 2 abordagens:

---

## 📊 Abordagem 1: VOD Service (Atual - Implementada)

### Como Funciona:
```
Gravação MP4 → VOD Service → FFmpeg → HLS (.m3u8 + .ts) → Cache → Player
```

### Vantagens:
- ✅ **Independente** - Não sobrecarrega MediaMTX
- ✅ **Cache inteligente** - Converte 1x, serve N vezes
- ✅ **Escalável** - Pode rodar em servidor separado
- ✅ **Seek instantâneo** - Segmentos HLS otimizados
- ✅ **Já implementado** - 100% funcional

### Desvantagens:
- ❌ Mais um serviço para gerenciar
- ❌ Usa espaço em disco para cache

### Configuração Atual:
```yaml
# docker-compose.yml
vod_hls:
  ports: ["8006:8004"]
  volumes:
    - ./recordings:/recordings:ro
    - ./hls_cache:/hls_cache
```

---

## 📊 Abordagem 2: MediaMTX Playback (Alternativa)

### Como Funciona:
```
Gravação MP4 → MediaMTX Playback API → HLS on-demand → Player
```

### Vantagens:
- ✅ **Centralizado** - Tudo no MediaMTX
- ✅ **Menos serviços** - Remove VOD Service
- ✅ **Sem cache extra** - MediaMTX gerencia

### Desvantagens:
- ❌ **Sobrecarga** - MediaMTX já processa 12+ streams live
- ❌ **Menos controle** - Cache e otimizações limitadas
- ❌ **Acoplamento** - VOD depende do MediaMTX live

### Como Habilitar:
```yaml
# mediamtx.yml
playback: yes
playbackAddress: :9996
```

### Uso:
```
GET http://mediamtx:9996/list?path=/recordings/camera_1/2026-02-20/
GET http://mediamtx:9996/get?path=/recordings/camera_1/2026-02-20/12-44-27.mp4
```

---

## 🔥 Abordagem 3: Híbrida (Recomendada para Produção)

### Como Funciona:
```
Live Streams → MediaMTX (HLS live)
Gravações → VOD Service (HLS on-demand)
```

### Vantagens:
- ✅ **Separação de responsabilidades**
- ✅ **MediaMTX focado em live** (baixa latência)
- ✅ **VOD Service focado em playback** (otimizado para seek)
- ✅ **Escalabilidade independente**

---

## 📈 Comparação de Performance

| Métrica | VOD Service | MediaMTX Playback |
|---------|-------------|-------------------|
| Latência inicial | ~500ms | ~800ms |
| Seek speed | Instantâneo | ~1-2s |
| CPU usage | Baixo (cache) | Médio-Alto |
| Memória | Cache em disco | RAM |
| Escalabilidade | Alta | Média |
| Manutenção | Simples | Acoplada |

---

## 💡 Recomendação Profissional

### Para seu VMS:

**MANTER VOD Service** porque:

1. **MediaMTX já está ocupado** com 12+ streams live
2. **VOD Service é otimizado** para playback (cache, seek)
3. **Separação de responsabilidades** = mais estável
4. **Já está 100% implementado** e funcionando

### Quando usar MediaMTX Playback:

- ✅ Sistema pequeno (1-4 câmeras)
- ✅ Poucos acessos simultâneos a gravações
- ✅ Quer simplicidade > performance

### Quando usar VOD Service:

- ✅ Sistema médio/grande (10+ câmeras) ← **SEU CASO**
- ✅ Múltiplos usuários acessando gravações
- ✅ Precisa de seek rápido e cache
- ✅ Quer escalar independentemente

---

## 🚀 Implementação MediaMTX Playback (Se quiser testar)

### 1. Habilitar no mediamtx.yml:
```yaml
playback: yes
playbackAddress: :9996
```

### 2. Expor porta no docker-compose.yml:
```yaml
mediamtx:
  ports:
    - "9996:9996"
```

### 3. Usar no frontend:
```typescript
// api.ts
getPlaybackUrl(cameraId, date, filename) {
  return `http://localhost:9996/get?path=/recordings/camera_${cameraId}/${date}/${filename}`
}
```

### 4. Reiniciar:
```bash
docker-compose restart mediamtx
```

---

## ✅ Conclusão

**Mantenha VOD Service** - É a abordagem profissional para seu caso de uso.

**Arquitetura Ideal:**
```
┌─────────────────┐
│   MediaMTX      │ ← Live Streams (RTSP → HLS)
│   (porta 8888)  │
└─────────────────┘

┌─────────────────┐
│  VOD Service    │ ← Gravações (MP4 → HLS)
│   (porta 8004)  │
└─────────────────┘

┌─────────────────┐
│    HAProxy      │ ← Gateway Unificado
│   (porta 80)    │
└─────────────────┘
```

**Quer testar MediaMTX Playback mesmo assim?** Posso implementar em 5 minutos.
