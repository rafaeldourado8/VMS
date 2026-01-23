# Google Maps Integration - Dashboard

## O que foi implementado

Dashboard com mapa interativo do Google Maps mostrando localização das câmeras em tempo real.

### Componentes

1. **CameraMap** (`src/components/map/CameraMap.tsx`)
   - Mapa interativo com Google Maps
   - Marcadores coloridos por status (verde=online, vermelho=offline)
   - InfoWindow com detalhes da câmera ao clicar
   - Suporte a múltiplas câmeras

2. **DashboardPage** (atualizado)
   - Mapa em destaque no topo
   - Layout reorganizado: Mapa → Gráficos → Atividade Recente

### Dependências

```json
{
  "@vis.gl/react-google-maps": "^1.0.0"
}
```

### Configuração

1. **Obter API Key do Google Maps:**
   - Acesse: https://console.cloud.google.com/google/maps-apis
   - Crie um projeto
   - Ative "Maps JavaScript API"
   - Crie credenciais (API Key)
   - Restrinja a chave ao seu domínio

2. **Configurar .env:**
```bash
VITE_GOOGLE_MAPS_API_KEY=sua_chave_aqui
```

3. **Adicionar latitude/longitude nas câmeras:**
```typescript
{
  id: 1,
  name: "Câmera 01",
  latitude: -15.7942,
  longitude: -47.8822,
  // ...
}
```

## Features

- ✅ Marcadores customizados (ícone de câmera)
- ✅ Cores por status (online/offline)
- ✅ InfoWindow com detalhes
- ✅ Centralização automática
- ✅ Zoom configurável
- ✅ Responsivo

## Uso

```tsx
<CameraMap
  cameras={cameras}
  apiKey={import.meta.env.VITE_GOOGLE_MAPS_API_KEY}
  center={{ lat: -15.7942, lng: -47.8822 }}
  zoom={12}
/>
```

## Custos

Google Maps API é **gratuito** até:
- 28.000 carregamentos de mapa/mês
- $200 de crédito mensal

Para VMS com ~20 usuários = ~600 carregamentos/mês = **$0/mês**
