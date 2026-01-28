# ✅ DVR-Lite - Checklist Completo

Roadmap completo para implementação da versão DVR-Lite.

**Cenário:** 1 VPS | 50 câmeras | 1 admin + 100 sub-users | $88/mês

**Tempo estimado:** 4-6 semanas

---

## 📚 Documentação

- **[SPECS.md](SPECS.md)** - Especificações técnicas detalhadas
- **[README.md](README.md)** - Documentação principal do DVR-Lite
- **[OVERVIEW.md](OVERVIEW.md)** - Visão geral do projeto
- **[SPRINT0_EXECUTIVE_SUMMARY.md](SPRINT0_EXECUTIVE_SUMMARY.md)** - Resumo executivo do Sprint 0
- **[SPRINT0_SUMMARY.md](SPRINT0_SUMMARY.md)** - Detalhes técnicos do Sprint 0
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Guia completo de testes
- **[GIT_COMMANDS.md](GIT_COMMANDS.md)** - Comandos Git para commit

---

## 🌿 Sprint 0: Branch Setup (2-3 dias)

### Criar Branch e Limpar Código
- [x] Criar branch `dvr-lite` a partir da `main`
- [x] Remover serviço `lpr_detection` do docker-compose.yml
- [x] Remover imports de IA no backend (YOLO, OCR, Rekognition)
- [x] Remover rotas de detecção no backend
- [x] Remover componentes de dashboard de detecções no frontend
- [x] Remover dependências de IA do requirements.txt
- [x] Atualizar .env.example (remover variáveis de IA)
- [x] Criar documentação (SPECS.md, GOVERNANCE.md)
- [x] **Testar que streaming ainda funciona** ✅ Backend rodando, RabbitMQ healthy
- [ ] **Commit: "chore: setup dvr-lite branch"** (executar comandos abaixo)

---

## 📹 Sprint 1: Recording Service (1 semana)

### Backend - Recording Service
- [ ] Criar `services/recording/` directory
- [ ] Criar `recording_service.py` com FFmpeg
- [ ] Implementar gravação contínua de streams HLS
- [ ] Configurar formato de arquivo (MP4/TS)
- [ ] Implementar rotação de arquivos por hora/dia
- [ ] Criar models: `Recording` (camera_id, start_time, end_time, file_path, size)
- [ ] Criar API endpoint: `GET /api/recordings/` (listar gravações)
- [ ] Criar API endpoint: `GET /api/recordings/{id}/` (detalhes)

### Storage
- [ ] Configurar S3 bucket para gravações
- [ ] Implementar upload para S3 (boto3)
- [ ] Criar estrutura de pastas: `recordings/{camera_id}/{date}/`
- [ ] Implementar fallback para storage local

### Limpeza Automática (7 dias)
- [ ] Criar Celery task: `cleanup_old_recordings`
- [ ] Implementar lógica de deleção (recordings > 7 dias)
- [ ] Agendar task diária (Celery Beat)
- [ ] Adicionar logs de limpeza
- [ ] Proteger clipes permanentes da limpeza

### Testes
- [ ] Testar gravação de 1 câmera
- [ ] Testar gravação de múltiplas câmeras
- [ ] Testar limpeza automática
- [ ] Testar upload S3
- [ ] Verificar uso de disco/banda

### Documentação
- [ ] Criar `docs/dvr-lite/recording/RECORDING.md`
- [ ] Documentar configuração de storage
- [ ] Documentar formato de arquivos

---

## ⏯️ Sprint 2: Playback & Timeline (1-2 semanas)

### Backend - Playback API
- [ ] Criar endpoint: `GET /api/playback/{camera_id}/` (listar gravações por câmera)
- [ ] Criar endpoint: `GET /api/playback/{camera_id}/date/{date}/` (gravações por data)
- [ ] Criar endpoint: `GET /api/playback/stream/{recording_id}/` (stream de playback)
- [ ] Implementar range requests (HTTP 206) para seek
- [ ] Implementar proxy de S3 para streaming
- [ ] Adicionar cache de metadados (Redis)

### Frontend - Video Player
- [ ] Criar componente `VideoPlayer.tsx`
- [ ] Integrar video.js ou plyr.io
- [ ] Implementar controles: play, pause, seek, volume
- [ ] Implementar fullscreen
- [ ] Adicionar loading states
- [ ] Adicionar error handling

### Frontend - Timeline Component
- [ ] Criar componente `Timeline.tsx`
- [ ] Implementar visualização de 24h
- [ ] Marcar períodos com gravação (barras azuis)
- [ ] Implementar navegação por data (date picker)
- [ ] Implementar zoom (1h, 6h, 12h, 24h)
- [ ] Implementar click para seek no vídeo
- [ ] Adicionar tooltips com horários

### Frontend - Playback Page
- [ ] Criar página `/playback/:cameraId`
- [ ] Layout: player (70%) + timeline (30%)
- [ ] Adicionar seletor de câmera
- [ ] Adicionar seletor de data
- [ ] Sincronizar player com timeline
- [ ] Adicionar botão "Criar Clipe"

### Testes
- [ ] Testar playback de gravações
- [ ] Testar seek em vídeos longos
- [ ] Testar navegação por timeline
- [ ] Testar múltiplas câmeras
- [ ] Testar performance com 20 câmeras

### Documentação
- [ ] Criar `docs/dvr-lite/playback/PLAYBACK.md`
- [ ] Documentar API de playback
- [ ] Documentar componentes de UI

---

## ✂️ Sprint 3: Clip System (1 semana)

### Backend - Clip API
- [ ] Criar model: `Clip` (recording_id, start_time, end_time, duration, name, created_by)
- [ ] Criar endpoint: `POST /api/clips/` (criar clipe)
- [ ] **Validar duração máxima: 5 minutos (300 segundos)**
- [ ] Criar endpoint: `GET /api/clips/` (listar clipes)
- [ ] Criar endpoint: `GET /api/clips/{id}/` (detalhes)
- [ ] Criar endpoint: `DELETE /api/clips/{id}/` (deletar clipe)
- [ ] Criar endpoint: `GET /api/clips/{id}/download/` (download)

### Backend - Clip Processing
- [ ] Criar Celery task: `create_clip`
- [ ] Implementar recorte com FFmpeg (start/end time)
- [ ] **Validar que duração não exceda 5 minutos**
- [ ] Salvar clipe em S3 (pasta separada: `clips/`)
- [ ] Adicionar flag `is_permanent=True` no banco
- [ ] Implementar fila de processamento
- [ ] Adicionar notificação quando clipe estiver pronto

### Frontend - Clip Creation
- [ ] Criar modal `CreateClipModal.tsx`
- [ ] Adicionar seleção de início/fim na timeline
- [ ] **Validar duração máxima: 5 minutos**
- [ ] **Mostrar contador de duração selecionada**
- [ ] **Bloquear seleção > 5 minutos**
- [ ] Adicionar preview do trecho selecionado
- [ ] Adicionar campo de nome do clipe
- [ ] Implementar criação de clipe
- [ ] Mostrar progresso de processamento

### Frontend - Clip Management
- [ ] Criar página `/clips`
- [ ] Listar todos os clipes (grid/lista)
- [ ] Adicionar thumbnail de cada clipe
- [ ] Mostrar duração do clipe
- [ ] Adicionar botão de play (abrir player)
- [ ] Adicionar botão de download
- [ ] Adicionar botão de deletar
- [ ] Adicionar filtros (câmera, data, usuário)

### Testes
- [ ] Testar criação de clipe curto (30s)
- [ ] Testar criação de clipe máximo (5min)
- [ ] **Testar validação de clipe > 5min (deve rejeitar)**
- [ ] Testar download de clipe
- [ ] Testar deleção de clipe
- [ ] Verificar que clipes não são deletados na limpeza

### Documentação
- [ ] Criar `docs/dvr-lite/clips/CLIPS.md`
- [ ] Documentar API de clipes
- [ ] **Documentar limite de 5 minutos**
- [ ] Documentar processamento FFmpeg

---

## 👥 Sprint 4: Multi-Usuário (1 semana)

### Backend - Sub-Users
- [ ] Atualizar model `User`: adicionar `parent_user_id` (FK)
- [ ] Criar endpoint: `POST /api/users/sub-users/` (criar sub-usuário)
- [ ] Criar endpoint: `GET /api/users/sub-users/` (listar sub-usuários)
- [ ] Criar endpoint: `PUT /api/users/sub-users/{id}/` (editar)
- [ ] Criar endpoint: `DELETE /api/users/sub-users/{id}/` (deletar)
- [ ] Implementar permissões: sub-user só vê câmeras do parent

### Backend - Permissions
- [ ] Criar model: `UserPermission` (user_id, camera_id, can_view, can_playback, can_clip)
- [ ] Implementar middleware de permissões
- [ ] Validar acesso em todas as rotas
- [ ] Adicionar filtros por permissão

### Frontend - User Management
- [ ] Criar página `/settings/users`
- [ ] Listar sub-usuários (tabela)
- [ ] Adicionar botão "Criar Sub-Usuário"
- [ ] Criar modal `CreateSubUserModal.tsx`
- [ ] Adicionar campos: nome, email, senha
- [ ] Adicionar seleção de câmeras permitidas
- [ ] Adicionar toggle de permissões
- [ ] Implementar edição de sub-usuário
- [ ] Implementar deleção de sub-usuário

### Frontend - Login
- [ ] Atualizar login para aceitar sub-usuários
- [ ] Mostrar nome do usuário logado
- [ ] Filtrar câmeras por permissão
- [ ] Adicionar indicador visual (parent vs sub-user)

### Testes
- [ ] Testar criação de sub-usuário
- [ ] Testar login como sub-usuário
- [ ] Testar permissões de câmeras
- [ ] Testar que sub-user não vê outras câmeras
- [ ] Testar deleção de sub-usuário

### Documentação
- [ ] Criar `docs/dvr-lite/users/MULTI_USER.md`
- [ ] Documentar sistema de permissões
- [ ] Documentar hierarquia de usuários

---

## ☁️ Sprint 5: Deploy AWS (1 semana)

### Infraestrutura
- [ ] Criar conta AWS (se necessário)
- [ ] Configurar IAM roles e policies
- [ ] Criar VPC e subnets
- [ ] Configurar Security Groups

### Storage (S3)
- [ ] Criar bucket S3 para gravações
- [ ] Criar bucket S3 para clipes
- [ ] Configurar lifecycle policy (7 dias)
- [ ] Configurar CORS
- [ ] Configurar CloudFront (opcional)

### Database (RDS)
- [ ] Criar instância RDS PostgreSQL (db.t3.small)
- [ ] Configurar backup automático
- [ ] Configurar security group
- [ ] Migrar schema

### Cache (ElastiCache)
- [ ] Criar instância Redis (cache.t3.micro)
- [ ] Configurar security group

### Compute (EC2 ou ECS)
- [ ] Opção A: EC2 t3.large com Docker Compose
- [ ] Opção B: ECS Fargate com task definitions
- [ ] Configurar auto-scaling (opcional)
- [ ] Configurar health checks

### Load Balancer
- [ ] Criar Application Load Balancer
- [ ] Configurar target groups
- [ ] Configurar SSL/TLS (ACM)
- [ ] Configurar domínio (Route 53)

### CI/CD
- [ ] Configurar GitHub Actions ou CodePipeline
- [ ] Criar workflow de deploy
- [ ] Configurar secrets

### Monitoring
- [ ] Configurar CloudWatch logs
- [ ] Configurar CloudWatch metrics
- [ ] Configurar alarmes (CPU, memória, disco)
- [ ] Configurar SNS para notificações

### Testes de Carga
- [ ] Testar streaming de 20 câmeras simultâneas
- [ ] Testar playback de múltiplos usuários
- [ ] Testar criação de clipes
- [ ] Monitorar custos

### Documentação
- [ ] Criar `docs/dvr-lite/deploy/AWS_DEPLOY.md`
- [ ] Documentar arquitetura AWS
- [ ] Documentar custos estimados
- [ ] Criar guia de troubleshooting

---

## 📊 Sprint 6: Polimento & Otimização (1 semana - Opcional)

### Performance
- [ ] Otimizar queries do banco
- [ ] Adicionar índices necessários
- [ ] Implementar cache agressivo
- [ ] Otimizar bundle do frontend
- [ ] Implementar lazy loading de componentes

### UX/UI
- [ ] Adicionar loading skeletons
- [ ] Melhorar feedback de erros
- [ ] Adicionar tooltips
- [ ] Melhorar responsividade mobile
- [ ] Adicionar dark mode (opcional)

### Segurança
- [ ] Implementar rate limiting
- [ ] Adicionar CSRF protection
- [ ] Validar inputs
- [ ] Sanitizar outputs
- [ ] Configurar HTTPS obrigatório

### Testes
- [ ] Testes unitários (backend)
- [ ] Testes de integração
- [ ] Testes E2E (Playwright/Cypress)
- [ ] Testes de carga (Locust/k6)

### Documentação Final
- [ ] Atualizar README.md
- [ ] Criar guia de usuário
- [ ] Criar guia de administrador
- [ ] Documentar API completa (Swagger)
- [ ] Criar vídeo demo

---

## 🎯 Critérios de Conclusão

### Funcional
- ✅ Streaming ao vivo funciona
- ✅ Gravação contínua por 7 dias
- ✅ Playback com timeline navegável
- ✅ Criar e gerenciar clipes (máx 5min)
- ✅ Sub-usuários com permissões
- ✅ Deploy AWS estável

### Performance
- ✅ Suporta 20 câmeras simultâneas
- ✅ Playback sem lag
- ✅ Timeline responsiva
- ✅ Clipes processam em < 1min

### Custos
- ✅ AWS < $200/mês (20 câmeras)
- ✅ Storage otimizado
- ✅ Banda otimizada

---

## 📈 Métricas de Sucesso

- **Uptime:** > 99%
- **Latência streaming:** < 3s
- **Latência playback:** < 1s
- **Tempo criação clipe:** < 1min (5min máx)
- **Custo por câmera:** < $10/mês

---

## 🔄 Próximos Passos

Após conclusão do DVR-Lite:
1. Coletar feedback de usuários
2. Iterar melhorias
3. Considerar merge de features para `main`
4. Avaliar adicionar IA opcional (toggle)
