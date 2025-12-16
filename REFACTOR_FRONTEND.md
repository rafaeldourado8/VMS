# 🎯 Plano de Refatoração Frontend - Performance

## 📊 Análise Atual

### Problemas Identificados
1. **47 componentes Radix UI** - Muitos não usados
2. **Sem lazy loading** - Todas páginas carregam de uma vez
3. **Bibliotecas pesadas**:
   - `@react-google-maps/api` (500KB+)
   - `leaflet` + `react-leaflet` (duplicado com Google Maps)
   - `framer-motion` (100KB+)
   - `recharts` (200KB+)
   - `xlsx` (500KB+)
4. **Sem code splitting** - Bundle único gigante
5. **Sem tree shaking otimizado**

## 🎯 Metas
- Bundle principal: <200KB (gzipped)
- Chunks de rotas: <100KB cada
- First Load: <2s
- Lighthouse: >90

## 📋 Ações Prioritárias

### 1. Lazy Loading de Rotas ⚡
```typescript
// App.tsx
const Dashboard = lazy(() => import('./pages/Dashboard'));
const LiveCameras = lazy(() => import('./pages/LiveCameras'));
const Detections = lazy(() => import('./pages/Detections'));
const CameraManagement = lazy(() => import('./pages/CameraManagement'));
const UserManagement = lazy(() => import('./pages/UserManagement'));
const Support = lazy(() => import('./pages/Support'));
```

### 2. Remover Bibliotecas Duplicadas 🗑️
- ❌ Remover `leaflet` + `react-leaflet` (usar só Google Maps)
- ❌ Remover `@react-google-maps/api` (usar `@googlemaps/js-api-loader` direto)
- ❌ Remover `framer-motion` (usar CSS animations)
- ❌ Remover `xlsx` (fazer export no backend)

### 3. Otimizar Radix UI 📦
Manter apenas componentes usados:
- ✅ dialog, dropdown-menu, select, switch, tabs, toast
- ❌ Remover: accordion, alert-dialog, aspect-ratio, avatar, calendar, carousel, chart, checkbox, collapsible, command, context-menu, drawer, hover-card, input-otp, menubar, navigation-menu, pagination, popover, progress, radio-group, resizable, scroll-area, separator, sheet, sidebar, skeleton, slider, toggle, toggle-group, tooltip

### 4. Code Splitting Vite 🔧
```typescript
// vite.config.ts
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        'vendor-react': ['react', 'react-dom', 'react-router-dom'],
        'vendor-ui': ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu'],
        'vendor-query': ['@tanstack/react-query', 'axios'],
        'vendor-video': ['hls.js']
      }
    }
  },
  chunkSizeWarningLimit: 500
}
```

### 5. Otimizar VideoPlayer 🎬
```typescript
// Lazy load HLS.js apenas quando necessário
const loadHls = () => import('hls.js');

// Usar IntersectionObserver para carregar players visíveis
const VideoPlayer = ({ src }) => {
  const [isVisible, setIsVisible] = useState(false);
  
  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setIsVisible(true);
        observer.disconnect();
      }
    });
    
    observer.observe(videoRef.current);
    return () => observer.disconnect();
  }, []);
  
  return isVisible ? <ActualPlayer src={src} /> : <Skeleton />;
};
```

### 6. Otimizar Imports 📥
```typescript
// ❌ Ruim
import { Button, Card, Input } from '@/components/ui';

// ✅ Bom (tree-shaking)
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
```

## 🚀 Implementação

### Fase 1: Limpeza (30min) ✅
- [x] Remover leaflet/react-leaflet
- [x] Remover framer-motion
- [x] Remover xlsx
- [x] Remover componentes Radix não usados (21 pacotes)
- [x] Limpar imports não utilizados

### Fase 2: Lazy Loading (20min) ✅
- [x] Implementar lazy loading em App.tsx (8 páginas)
- [x] Adicionar Suspense com fallback (spinner)
- [x] Testar navegação entre rotas

### Fase 3: Code Splitting (15min) ✅
- [x] Configurar manualChunks no vite.config.ts (8 chunks)
- [x] Minificação terser (drop console/debugger)
- [x] chunkSizeWarningLimit: 500KB

### Fase 4: Otimizar VideoPlayer (30min) ✅
- [x] Implementar IntersectionObserver (rootMargin: 50px)
- [x] Lazy load HLS.js (import dinâmico)
- [x] Players só carregam quando visíveis

### Fase 5: Validação (15min) ✅
- [x] Build de produção (npm run build)
- [x] Bundle principal: 17.74 kB gzipped
- [x] Total: ~340 kB (83% redução)
- [x] Code splitting: 8 chunks + lazy pages

## 📈 Resultados Esperados

| Métrica | Antes | Depois | Melhoria |
|---------|-------|--------|----------|
| Bundle principal | ~2MB | <200KB | 90% |
| First Load | ~5s | <2s | 60% |
| Lighthouse | ~60 | >90 | 50% |
| Componentes UI | 47 | ~10 | 80% |
| Dependencies | 70 | ~40 | 43% |

## ⚠️ Cuidados
- Não quebrar funcionalidades existentes
- Testar cada página após mudanças
- Manter UX consistente
- Documentar breaking changes
