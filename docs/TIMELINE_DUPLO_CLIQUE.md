# Timeline com Duplo Clique

## 📋 Funcionalidade Implementada

A timeline de playback agora aparece apenas quando necessário, evitando múltiplas requisições desnecessárias.

## 🎯 Comportamento

### CameraCard (Grid)
- **Clique simples**: Abre o modal de visualização da câmera (comportamento padrão)
- **Duplo clique**: Abre o modal E ativa a timeline automaticamente

### Modal de Câmera
- **Botão "Mostrar Timeline"**: Alterna a visibilidade da timeline manualmente
- **Timeline oculta por padrão**: Evita requisições desnecessárias ao abrir o modal
- **Modo Live/Playback**: Alterna entre visualização ao vivo e gravações

## 🔧 Componentes Modificados

### 1. CameraCard.tsx
```typescript
// Detecta duplo clique
const handleClick = () => {
  if (clickTimeoutRef.current) {
    // Duplo clique detectado
    clearTimeout(clickTimeoutRef.current)
    clickTimeoutRef.current = null
    onDoubleClick?.()
  } else {
    // Primeiro clique - aguarda segundo clique
    clickTimeoutRef.current = setTimeout(() => {
      clickTimeoutRef.current = null
      onClick?.()
    }, 300)
  }
}
```

### 2. CameraGrid.tsx
```typescript
interface CameraGridProps {
  cameras: Camera[]
  onCameraClick?: (camera: Camera) => void
  onCameraDoubleClick?: (camera: Camera) => void  // Nova prop
  onCameraDelete?: (camera: Camera) => void
}
```

### 3. CamerasPage.tsx
```typescript
// Estado para controlar timeline
const [showTimeline, setShowTimeline] = useState(false)

// Timeline só carrega gravações quando visível
useEffect(() => {
  if (showTimeline) {
    fetchRecordings()
  }
}, [showTimeline])
```

## 📊 Fluxo de Uso

### Cenário 1: Visualização Rápida (Clique Simples)
```
1. Usuário clica na câmera no grid
2. Modal abre com vídeo ao vivo
3. Timeline NÃO é carregada
4. Sem requisições extras
```

### Cenário 2: Análise de Gravações (Duplo Clique)
```
1. Usuário dá duplo clique na câmera
2. Modal abre com vídeo ao vivo
3. Timeline é ativada automaticamente
4. Gravações são carregadas
5. Usuário pode navegar no histórico
```

### Cenário 3: Ativação Manual
```
1. Usuário abre modal (clique simples)
2. Clica em "Mostrar Timeline"
3. Timeline aparece
4. Gravações são carregadas sob demanda
```

## ⚡ Otimizações

### Antes (Problema)
- Timeline sempre visível
- Requisições automáticas ao abrir modal
- Múltiplas chamadas à API de gravações
- Consumo desnecessário de recursos

### Depois (Solução)
- Timeline oculta por padrão
- Requisições apenas quando necessário
- Carregamento sob demanda
- Melhor performance

## 🎨 Interface

### Botão Toggle Timeline
```tsx
<Button
  variant="outline"
  size="sm"
  onClick={() => setShowTimeline(!showTimeline)}
  className="w-full"
>
  {showTimeline ? 'Ocultar Timeline' : 'Mostrar Timeline'}
</Button>
```

### Indicador de Modo
```tsx
{mode === 'playback' && (
  <button onClick={goLive} className="...">
    <Radio className="w-4 h-4" />
    Ao Vivo
  </button>
)}
```

## 🔄 Estados da Timeline

| Estado | Descrição | Requisições |
|--------|-----------|-------------|
| Oculta | Padrão ao abrir modal | Nenhuma |
| Visível (Live) | Mostra linha do tempo atual | Busca gravações do dia |
| Visível (Playback) | Navegando no histórico | Busca segmento específico |

## 📝 Notas de Implementação

1. **Timeout de 300ms**: Tempo para detectar duplo clique
2. **useRef para timeout**: Evita re-renders desnecessários
3. **Lazy loading**: Gravações carregadas apenas quando timeline visível
4. **Cleanup**: Timeout limpo ao desmontar componente

## 🚀 Próximas Melhorias

- [ ] Adicionar atalho de teclado (ex: 'T' para toggle timeline)
- [ ] Salvar preferência do usuário (timeline sempre visível/oculta)
- [ ] Pré-carregar gravações em background (opcional)
- [ ] Adicionar loading state ao ativar timeline
- [ ] Tooltip explicando duplo clique

## 🐛 Troubleshooting

### Timeline não aparece
- Verificar se há gravações disponíveis
- Checar endpoint `/api/cameras/{id}/recordings/{date}/`
- Validar formato de resposta da API

### Duplo clique não funciona
- Verificar se `onDoubleClick` está sendo passado
- Ajustar timeout (300ms pode ser muito rápido/lento)
- Testar em diferentes dispositivos

### Performance
- Timeline carrega apenas quando visível
- Gravações são cacheadas
- Requisições são canceladas ao fechar modal
