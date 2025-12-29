# 🎥 Comportamento Normal do Player HLS

## ✅ Primeiro Request "Cancelado" é NORMAL

### 📋 O que acontece:
```
index.m3u8 (cancelado) ← NORMAL - Stream ainda não existe
index.m3u8 200 ← Stream criado e funcionando
video1_stream.m3u8 200 ← Segmentos carregando normalmente
```

### 🔄 Fluxo Normal de Inicialização:

1. **Player solicita manifest** → `index.m3u8`
2. **MediaMTX detecta demanda** → Inicia conexão RTSP
3. **Primeiro request falha** → Stream ainda não pronto (NORMAL)
4. **MediaMTX conecta à câmera** → ~10-15 segundos
5. **Stream fica disponível** → Requests subsequentes funcionam
6. **Player funciona normalmente** → Vídeo reproduz

### ⚡ Otimizações Aplicadas:

#### Player Frontend:
```javascript
// Retry automático para erro 404 inicial
this.hls.on(window.Hls.Events.MANIFEST_LOAD_ERROR, (event, data) => {
    if (data.response?.code === 404) {
        console.log('⏳ Stream ainda não disponível, tentando novamente...');
        setTimeout(() => {
            if (!this.isDestroyed && this.hls) {
                this.hls.loadSource(this.streamUrl);
            }
        }, 2000);
    }
});
```

#### MediaMTX:
```yaml
sourceOnDemandStartTimeout: 15s  # Reduzido para inicializar mais rápido
sourceOnDemandCloseAfter: 20s    # Fecha rapidamente quando não usado
```

### 🎯 Sinais de Funcionamento Normal:

✅ **Primeiro request cancelado** - Stream sendo criado  
✅ **Segundo request 200** - Stream pronto  
✅ **Requests subsequentes 200** - Funcionando normalmente  
✅ **Tempo de inicialização: 10-15s** - Normal para streams on-demand  

### 🚨 Quando se Preocupar:

❌ **Todos os requests falhando** - Problema na câmera/rede  
❌ **Timeout > 30s** - Câmera não responde  
❌ **Requests 500** - Erro interno do MediaMTX  

### 📊 Logs Normais:
```
MediaMTX:
[HLS] [muxer cam_1] created (requested by client)
[path cam_1] [RTSP source] started on demand
[path cam_1] [RTSP source] ready: 1 track (H264)

Player:
📡 Carregando manifest...
⏳ Stream ainda não disponível, tentando novamente...
🎥 Player anexado ao elemento de vídeo
📋 Manifest carregado, iniciando reprodução
```

---

**Conclusão:** O primeiro request cancelado é **comportamento normal** para streams on-demand. O sistema está funcionando corretamente!