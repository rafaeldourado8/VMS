# Correções de Memória e Storage - VMS

## Problemas Identificados

1. **QuotaExceededError no localStorage** - Snapshots de câmeras em base64 excediam limite de 5-10MB
2. **Stream crashando após 1 hora** - Memory leak por acúmulo de buffers HLS
3. **Sem limpeza de cache** - Dados antigos nunca eram removidos

## Soluções Implementadas

### 1. IndexedDB para Snapshots (50MB+ storage)

**Arquivo:** `frontend/src/lib/snapshotCache.ts`

- Substitui localStorage por IndexedDB (limite muito maior)
- Auto-expira snapshots após 24h
- Função de limpeza automática de dados antigos

**Uso:**
```typescript
import { getSnapshot, setSnapshot, clearOldSnapshots } from '@/lib/snapshotCache'

// Buscar snapshot
const snapshot = await getSnapshot(cameraId)

// Salvar snapshot
await setSnapshot(cameraId, base64Data)

// Limpar antigos
await clearOldSnapshots()
```

### 2. Limpeza Automática de Snapshots

**Arquivo:** `frontend/src/hooks/useSnapshotCleanup.ts`

- Hook React que limpa snapshots antigos a cada 1 hora
- Executado automaticamente no App.tsx

### 3. Otimização de Buffers HLS

**Arquivo:** `frontend/src/components/cameras/VideoPlayer.tsx`

**Antes:**
```typescript
backBufferLength: 30,
maxBufferLength: 30,
maxBufferSize: 60 * 1000 * 1000, // 60MB
```

**Depois:**
```typescript
backBufferLength: 10,      // Reduzido de 30s para 10s
maxBufferLength: 20,       // Reduzido de 30s para 20s
maxBufferSize: 20 * 1000 * 1000, // Reduzido para 20MB
maxMaxBufferLength: 30,    // Limite máximo
```

### 4. Limpeza de Vídeo ao Desmontar

**Adicionado cleanup no useEffect:**
```typescript
return () => {
  if (video) {
    video.pause()
    video.src = ''
    video.load()  // Libera memória
  }
  hls.destroy()
  hlsRef.current = null
}
```

### 5. Reconexão Periódica (45min)

**Previne memory leak em streams longos:**
```typescript
useEffect(() => {
  const reconnectInterval = setInterval(() => {
    if (hlsRef.current && !error) {
      // Destroi e recria HLS instance
      hlsRef.current.destroy()
      // ... recria conexão
    }
  }, 45 * 60 * 1000) // 45 minutos
  
  return () => clearInterval(reconnectInterval)
}, [src, error])
```

## Arquivos Modificados

1. ✅ `frontend/src/lib/snapshotCache.ts` - CRIADO
2. ✅ `frontend/src/hooks/useSnapshotCleanup.ts` - CRIADO
3. ✅ `frontend/src/components/cameras/StreamThumbnail.tsx` - MODIFICADO
4. ✅ `frontend/src/components/cameras/VideoPlayer.tsx` - MODIFICADO
5. ✅ `frontend/src/App.tsx` - MODIFICADO

## Benefícios

- ✅ **Sem mais QuotaExceededError** - IndexedDB suporta 50MB+
- ✅ **Streams estáveis por horas** - Reconexão automática previne leaks
- ✅ **Menor uso de memória** - Buffers reduzidos de 60MB para 20MB
- ✅ **Limpeza automática** - Cache antigo removido periodicamente
- ✅ **Troca de câmera limpa** - Buffers liberados corretamente

## Testes Recomendados

1. Abrir múltiplas câmeras e verificar console (sem erros de quota)
2. Deixar stream aberto por 2+ horas (deve reconectar automaticamente)
3. Trocar entre câmeras rapidamente (sem acúmulo de memória)
4. Verificar DevTools > Application > IndexedDB > vms_snapshots
5. Monitorar uso de memória no Task Manager durante streaming longo

## Monitoramento

```javascript
// Ver tamanho do cache IndexedDB
const db = await indexedDB.open('vms_snapshots')
// Inspecionar em DevTools > Application > IndexedDB

// Ver uso de memória do HLS
console.log(hlsRef.current?.bufferController?.bufferInfo)
```
