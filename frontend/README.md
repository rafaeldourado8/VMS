# GT-Vision VMS Frontend

Frontend corporativo para o sistema GT-Vision VMS (Video Management System).

## 🚀 Tech Stack

- **React 18** + TypeScript
- **Vite** - Build tool ultrarrápido
- **Tailwind CSS** - Styling
- **React Query** - Data fetching & caching
- **Zustand** - State management
- **React Router** - Routing
- **Recharts** - Charts
- **HLS.js** - Video streaming
- **Lucide React** - Icons

## 📁 Estrutura

```
src/
├── components/
│   ├── ui/           # Componentes base (Button, Card, Input, etc)
│   ├── layout/       # Layout principal e navegação
│   ├── cameras/      # Componentes de câmera (VideoPlayer, CameraCard, Grid)
│   └── dashboard/    # Componentes do dashboard
├── pages/            # Páginas da aplicação
│   ├── LoginPage.tsx
│   ├── DashboardPage.tsx
│   ├── CamerasPage.tsx
│   ├── DetectionsPage.tsx
│   └── SettingsPage.tsx
├── services/         # API services
├── store/            # Zustand stores
├── hooks/            # Custom hooks
├── types/            # TypeScript types
└── lib/              # Utilities
```

## 🏃 Rodando Localmente

```bash
# Instalar dependências
npm install

# Rodar em desenvolvimento
npm run dev

# Build para produção
npm run build
```

## 🔧 Configuração

Copie `.env.example` para `.env` e ajuste as URLs conforme necessário:

```env
VITE_API_URL=http://localhost:8000
VITE_STREAMING_URL=http://localhost:8001
VITE_HLS_URL=http://localhost:8888
```

## 🐳 Docker

```bash
# Build da imagem
docker build -t gtvision-frontend .

# Rodar container
docker run -p 3000:80 gtvision-frontend
```

## 📱 Features

### Dashboard
- Estatísticas em tempo real
- Gráficos de detecções por hora
- Distribuição por tipo de veículo
- Atividade recente
- Preview de câmeras

### Câmeras
- Grid responsivo (1x1, 2x2, 3x3, 4x4)
- Player HLS com baixa latência
- Adicionar/remover câmeras
- Status em tempo real
- Modal de visualização expandida

### Detecções
- Listagem paginada
- Filtro por placa e câmera
- Detalhes da detecção
- Confiança do reconhecimento

### Configurações
- Perfil do usuário
- Status do sistema
- Notificações
- Aparência

## 🔒 Autenticação

O frontend usa JWT tokens armazenados no localStorage via Zustand persist.
- Access token para requisições
- Refresh token para renovação automática
- Logout limpa tokens e redireciona para login

## 🎨 Tema

Design system corporativo com tema escuro:
- Background: `hsl(222 47% 6%)`
- Primary: `hsl(210 100% 50%)` (azul)
- Cards com bordas sutis
- Tipografia Inter + JetBrains Mono

## 📡 Integração

- **API Backend (Django)**: `/api/*`
- **Streaming Service**: `/streaming/*`
- **MediaMTX HLS**: `/hls/*`
- **WebSocket Events**: `/ws/*`

Todas as rotas são proxificadas pelo Vite em dev e pelo Nginx em produção.
