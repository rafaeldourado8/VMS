# 📚 VMS - Índice de Documentação

## 📋 Documentação Principal

### Planejamento
- **[TASKS.md](TASKS.md)** - Tasks atualizadas e organizadas por fase
- **[TASKS_NEW.md](TASKS_NEW.md)** - Tasks detalhadas (backup)
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Resumo completo do projeto

### Arquitetura
- **[ARCHITECTURE_DIAGRAM.excalidraw.json](ARCHITECTURE_DIAGRAM.excalidraw.json)** - Diagrama visual da arquitetura
- **[STREAMING_FLOW.md](STREAMING_FLOW.md)** - Fluxo de streaming
- **[CONTEXT.md](CONTEXT.md)** - Contexto do projeto

### Testes
- **[TEST_FAILOVER.md](TEST_FAILOVER.md)** - Guia de teste de failover

---

## 🏗️ Arquitetura (Histórico)

### DDD & Refactoring
- [DDD_100_COMPLETE.md](architecture/DDD_100_COMPLETE.md)
- [DDD_COMPLETE_SUMMARY.md](architecture/DDD_COMPLETE_SUMMARY.md)
- [DDD_FINAL_COMPLETE.md](architecture/DDD_FINAL_COMPLETE.md)
- [DDD_REFACTORING_PLAN.md](architecture/DDD_REFACTORING_PLAN.md)

### Streaming
- [STREAMING_ARCHITECTURE.md](architecture/STREAMING_ARCHITECTURE.md)
- [HLS_BEHAVIOR.md](architecture/HLS_BEHAVIOR.md)

### Segurança
- [SECURITY.md](architecture/SECURITY.md)
- [SECURITY_IMPLEMENTATION.md](architecture/SECURITY_IMPLEMENTATION.md)

---

## 🔧 Guias Técnicos

### Setup & Deployment
- [12CAM_SETUP.md](12CAM_SETUP.md) - Setup de 12 câmeras
- [MIGRATION_PLAN.md](MIGRATION_PLAN.md) - Plano de migração
- [MIGRATION_COMPLETE.md](MIGRATION_COMPLETE.md) - Migração completa

### Otimização
- [CPU_OPTIMIZATION.md](CPU_OPTIMIZATION.md) - Otimização de CPU
- [ALTA_DISPONIBILIDADE.md](ALTA_DISPONIBILIDADE.md) - Alta disponibilidade

### Troubleshooting
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Resolução de problemas
- [CORREÇÕES_REALIZADAS.md](CORREÇÕES_REALIZADAS.md) - Correções aplicadas
- [CORREÇÃO_HLS_404.md](CORREÇÃO_HLS_404.md) - Fix HLS 404
- [CORREÇÃO_UPLOAD_IMAGENS.md](CORREÇÃO_UPLOAD_IMAGENS.md) - Fix upload

---

## 🤖 IA & Detecção

- [AI_DETECTION_SYSTEM.md](AI_DETECTION_SYSTEM.md) - Sistema de detecção IA

---

## 📊 Roadmaps & Status

- [ROADMAP.md](ROADMAP.md) - Roadmap geral
- [ROADMAP_15_DIAS_COMPLETO.md](ROADMAP_15_DIAS_COMPLETO.md) - Roadmap 15 dias
- [SYSTEM_STATUS.md](SYSTEM_STATUS.md) - Status do sistema

---

## 🧪 Testes

### Scripts de Teste (em `/tests`)
- `test_auto_restart.py` - Teste de auto-restart
- `test_failover.py` - Teste de failover
- `test_streaming_capacity.py` - Teste de capacidade
- `test_real_cameras.py` - Teste com câmeras reais

### Documentação de Testes
- [TESTE_CAMERAS_REAIS.md](../tests/TESTE_CAMERAS_REAIS.md)
- [TESTE_VIDEO_LOCAL.md](../tests/TESTE_VIDEO_LOCAL.md)
- [DRIFT_FIX_SUMMARY.md](../tests/DRIFT_FIX_SUMMARY.md)

---

## 📦 Serviços

### LPR Detection
- [services/lpr_detection/ADAPTATION.md](../services/lpr_detection/ADAPTATION.md)
- [services/lpr_detection/BUILD_OPTIMIZATION.md](../services/lpr_detection/BUILD_OPTIMIZATION.md)
- [services/lpr_detection/TEST_GUIDE.md](../services/lpr_detection/TEST_GUIDE.md)

### Streaming
- [services/streaming/README.md](../services/streaming/README.md)

---

## 🚀 Quick Start

1. **Entender o Projeto**: Leia [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
2. **Ver Arquitetura**: Abra [ARCHITECTURE_DIAGRAM.excalidraw.json](ARCHITECTURE_DIAGRAM.excalidraw.json) no Excalidraw
3. **Seguir Tasks**: Consulte [TASKS.md](TASKS.md)
4. **Testar**: Use guias em `/tests`

---

## 📝 Convenções

### Nomenclatura de Arquivos
- `UPPERCASE.md` - Documentação principal
- `lowercase.md` - Documentação técnica
- `PascalCase.md` - Guias específicos

### Organização
```
docs/
├── TASKS.md              # Tasks principais
├── PROJECT_SUMMARY.md    # Resumo do projeto
├── architecture/         # Docs de arquitetura
├── guides/              # Guias técnicos
└── INDEX.md             # Este arquivo
```

---

## 🔄 Atualizações

- **2025-01-XX**: Reorganização da documentação
- **2025-01-XX**: Adição de LPR Detection
- **2025-01-XX**: Nova arquitetura de gravação
