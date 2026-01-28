# 📹 DVR-Lite Documentation

Documentação completa da versão DVR-Lite do VMS - Sistema de gravação e reprodução sem detecção de IA.

---

## 🎯 Cenário de Uso

- **1 VPS** (servidor único)
- **50 câmeras** total
- **1 admin** + **100 sub-usuários**
- **Permissão:** 1 câmera por sub-usuário
- **Gravação:** 7 dias
- **Custo:** ~$88/mês ($0.88/usuário)

---

## 📚 Índice de Documentos

### Planejamento
- **[SPECS.md](SPECS.md)** - Especificações técnicas (50 câmeras, 100 usuários, 1 VPS)
- **[GOVERNANCE.md](GOVERNANCE.md)** - Governança e multi-tenant (Super Admin + Clientes)
- **[CHECKLIST.md](CHECKLIST.md)** - Roadmap completo com todas as tarefas
- **[OVERVIEW.md](OVERVIEW.md)** - Visão geral do projeto DVR-Lite

### Sprint 0: Branch Setup
- **[SPRINT0_SUMMARY.md](SPRINT0_SUMMARY.md)** - Resumo das mudanças do Sprint 0
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Guia completo de testes
- **[GIT_COMMANDS.md](GIT_COMMANDS.md)** - Comandos Git para commit

### Sprints Futuros
- Sprint 1: Recording Service (em breve)
- Sprint 2: Playback & Timeline (em breve)
- Sprint 3: Clip System (em breve)
- Sprint 4: Multi-Usuário (em breve)
- Sprint 5: Deploy AWS (em breve)

---

## 🎯 O que é DVR-Lite?

DVR-Lite é uma versão simplificada do VMS focada exclusivamente em:
- ✅ Streaming de câmeras (RTSP/RTMP)
- ✅ Gravação contínua (7 dias)
- ✅ Playback com timeline
- ✅ Sistema de clipes (máx 5 minutos)
- ✅ Multi-usuário com permissões
- ❌ **SEM** detecção de IA
- ❌ **SEM** reconhecimento de placas (LPR)
- ❌ **SEM** busca retroativa com IA

---

## 🚀 Quick Start

### 1. Clonar e configurar
```bash
git clone <repo-url>
cd VMS
git checkout dvr-lite
cp .env.example .env
```

### 2. Subir serviços
```bash
docker-compose up -d
```

### 3. Acessar
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Prometheus: http://localhost:9090

---

## 📋 Status do Projeto

### ✅ Sprint 0: Branch Setup (Concluído)
- [x] Remover serviços de IA
- [x] Limpar código backend
- [x] Limpar código frontend
- [x] Atualizar variáveis de ambiente
- [x] Documentar mudanças
- [x] Criar guia de testes

### 🔄 Sprint 1: Recording Service (Próximo)
- [ ] Implementar gravação contínua
- [ ] Configurar storage (S3/local)
- [ ] Implementar limpeza automática (7 dias)
- [ ] Criar API de listagem de gravações

### 📋 Sprints Futuros
Ver [CHECKLIST.md](CHECKLIST.md) para roadmap completo.

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│                    React + Vite + HLS.js                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend API                            │
│                   Django REST Framework                     │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
         ┌──────────┐  ┌──────────┐  ┌──────────┐
         │PostgreSQL│  │  Redis   │  │ RabbitMQ │
         └──────────┘  └──────────┘  └──────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       MediaMTX                              │
│                  HLS Streaming Server                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  RTSP/RTMP      │
                    │  Cameras        │
                    └─────────────────┘
```

---

## 🛠️ Stack Tecnológica

### Backend
- Django 5.1.4
- PostgreSQL 15
- Redis 7
- RabbitMQ 3.13
- Celery 5.3

### Frontend
- React 18
- Vite 5
- TypeScript
- TailwindCSS

### Streaming
- MediaMTX (HLS)
- FFmpeg (para gravação)

### Infraestrutura
- Docker Compose
- Prometheus (monitoring)

---

## 📊 Diferenças vs VMS Full

| Recurso | VMS Full | DVR-Lite |
|---------|----------|----------|
| Streaming | ✅ | ✅ |
| Gravação | ✅ | ✅ |
| Playback | ✅ | ✅ |
| Clipes | ✅ | ✅ (máx 5min) |
| Multi-usuário | ✅ | ✅ |
| Detecção LPR | ✅ | ❌ |
| Dashboard IA | ✅ | ❌ |
| Busca Retroativa | ✅ | ❌ |
| Blacklist | ✅ | ❌ |
| Analytics | ✅ | ❌ |
| Relatórios | ✅ | ❌ |

---

## 💰 Custos Estimados (1 VPS)

### VPS Recomendada (Hetzner CPX51)
- CPU: 8 cores
- RAM: 16 GB
- Disco: 360 GB NVMe
- Custo: €50/mês (~$55/mês)

### Storage Externo (Wasabi)
- 5 TB para gravações (7 dias)
- Custo: $30/mês

### Backup (Opcional)
- Backblaze B2: 500 GB
- Custo: $3/mês

### Total
- **VPS + Storage + Backup:** ~$88/mês
- **Por usuário:** $0.88/mês (100 usuários)
- **Por câmera:** $1.76/mês (50 câmeras)

Ver [SPECS.md](SPECS.md) para detalhes completos.

---

## 🧪 Testes

### Executar testes completos
```bash
# Ver guia de testes
cat docs/dvr-lite/TESTING_GUIDE.md

# Ou seguir checklist
# 1. Inicialização
docker-compose up -d
docker-compose ps

# 2. API
curl http://localhost:8000/health

# 3. Frontend
# Abrir http://localhost:5173
```

---

## 📝 Desenvolvimento

### Workflow
1. Escolher task do [CHECKLIST.md](CHECKLIST.md)
2. Criar branch (opcional): `git checkout -b feature/task-name`
3. Implementar com código mínimo
4. Testar localmente
5. Commit e push
6. Atualizar checklist

### Estrutura de Código
```
VMS/
├── backend/              # Django API
│   ├── apps/            # Apps Django
│   ├── config/          # Configurações
│   └── requirements.txt
├── frontend/            # React + Vite
│   ├── src/
│   └── package.json
├── services/
│   └── streaming/       # MediaMTX integration
├── docs/
│   └── dvr-lite/       # Esta documentação
└── docker-compose.yml
```

---

## 🔗 Links Úteis

### Documentação Principal
- [README.md](../../README.md) - README principal do VMS
- [SYSTEM_OVERVIEW.md](../SYSTEM_OVERVIEW.md) - Visão geral do sistema
- [TECH_STACK.md](../TECH_STACK.md) - Stack tecnológica

### Tecnologias
- [Django Docs](https://docs.djangoproject.com/)
- [React Docs](https://react.dev/)
- [MediaMTX Docs](https://github.com/bluenviron/mediamtx)
- [FFmpeg Docs](https://ffmpeg.org/documentation.html)

---

## 🤝 Contribuindo

1. Ler [CHECKLIST.md](CHECKLIST.md) para ver tarefas pendentes
2. Escolher uma task
3. Implementar seguindo o workflow
4. Testar usando [TESTING_GUIDE.md](TESTING_GUIDE.md)
5. Documentar mudanças
6. Commit usando [GIT_COMMANDS.md](GIT_COMMANDS.md)

---

## 📄 Licença

[Definir licença]

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar [TESTING_GUIDE.md](TESTING_GUIDE.md) - Troubleshooting
2. Ver logs: `docker-compose logs [service]`
3. Abrir issue no repositório
