# Organização da Documentação VMS

## 📁 Estrutura Atualizada

```
docs/
├── code-review/              # ⭐ NOVO - Resultados do Code Review
│   ├── backend/
│   ├── frontend/
│   ├── services/
│   ├── config/
│   ├── scripts/
│   ├── guides/              # Guias de correção
│   ├── INDEX.md             # Índice principal do code review
│   ├── SECURITY_ISSUES.md   # Vulnerabilidades de segurança
│   ├── CODE_QUALITY.md      # Problemas de qualidade
│   ├── INFRASTRUCTURE.md    # Problemas de infraestrutura
│   ├── PERFORMANCE.md       # Problemas de performance
│   └── DEPLOYMENT.md        # Riscos de deployment
│
├── mvp/                     # Documentação do MVP
│   ├── sprints/
│   ├── timeline/
│   └── *.md
│
├── backend/                 # Documentação do backend
├── frontend/                # Documentação do frontend
├── database/                # Documentação do banco de dados
├── gateway/                 # Documentação do gateway
├── mediamtx/                # Documentação do MediaMTX
├── recorder/                # Documentação do recorder
├── streaming/               # Documentação de streaming
├── protocolos/              # Documentação de protocolos
│   ├── hls/
│   ├── onvif/
│   ├── rtmp/
│   ├── rtsp/
│   └── webrtc/
│
├── diagrams/                # Diagramas de arquitetura
├── bugs/                    # Documentação de bugs
├── fixes/                   # Documentação de correções
├── scalability/             # Documentação de escalabilidade
│
└── *.md                     # Documentos gerais
```

## 📚 Documentos Principais

### Code Review (NOVO)
- [INDEX.md](./code-review/INDEX.md) - Índice principal do code review
- [SECURITY_ISSUES.md](./code-review/SECURITY_ISSUES.md) - Vulnerabilidades
- [CODE_QUALITY.md](./code-review/CODE_QUALITY.md) - Qualidade de código
- [INFRASTRUCTURE.md](./code-review/INFRASTRUCTURE.md) - Infraestrutura
- [PERFORMANCE.md](./code-review/PERFORMANCE.md) - Performance
- [DEPLOYMENT.md](./code-review/DEPLOYMENT.md) - Deployment

### Guias de Correção (NOVO)
- [FIX_SQL_INJECTION.md](./code-review/guides/FIX_SQL_INJECTION.md)
- [FIX_SECRETS.md](./code-review/guides/FIX_SECRETS.md)
- [FIX_CORS.md](./code-review/guides/FIX_CORS.md)
- [FIX_RATE_LIMITING.md](./code-review/guides/FIX_RATE_LIMITING.md)
- [FIX_QUERIES.md](./code-review/guides/FIX_QUERIES.md)

### Arquitetura
- [ARCHITECTURE_CHANGES.md](./ARCHITECTURE_CHANGES.md)
- [ARCHITECTURE_500_CAMERAS.md](./ARCHITECTURE_500_CAMERAS.md)
- [ELASTIC_ARCHITECTURE.md](./ELASTIC_ARCHITECTURE.md)

### Streaming
- [STREAMING_FALLBACK.md](./STREAMING_FALLBACK.md)
- [UNIFIED_HLS_STREAM.md](./UNIFIED_HLS_STREAM.md)
- [ZERO_BANDWIDTH_STREAMING.md](./ZERO_BANDWIDTH_STREAMING.md)

### Gravações
- [RECORDING_SYSTEM.md](./RECORDING_SYSTEM.md)
- [RECORDING_ARCHITECTURE.md](./RECORDING_ARCHITECTURE.md)
- [RECORDING_RETENTION.md](./RECORDING_RETENTION.md)

### Deploy & DevOps
- [AWS_EC2_SPOT_SETUP.md](./AWS_EC2_SPOT_SETUP.md)
- [DEPLOY_CHECKLIST.md](./DEPLOY_CHECKLIST.md)
- [EC2_START_STOP.md](./EC2_START_STOP.md)

### Segurança
- [LOGIN_SECURITY.md](./LOGIN_SECURITY.md)
- [RECORDING_SECURITY.md](./RECORDING_SECURITY.md)
- [IAM_BACKEND.md](./IAM_BACKEND.md)

### Performance
- [LOAD_TESTING.md](./LOAD_TESTING.md)
- [PLAYER_PERFORMANCE_OPTIMIZATION.md](./PLAYER_PERFORMANCE_OPTIMIZATION.md)
- [HLS_CHUNKS_OPTIMIZATION.md](./HLS_CHUNKS_OPTIMIZATION.md)

### Capacidade
- [CAPACITY_PLAN.md](./CAPACITY_PLAN.md)
- [SYSTEM_CAPACITY.md](./SYSTEM_CAPACITY.md)
- [STORAGE_CALCULATOR.md](./STORAGE_CALCULATOR.md)

## 🎯 Por Onde Começar

### Desenvolvedor Novo
1. [README.md](../README.md) - Visão geral do projeto
2. [mvp/INDEX.md](./mvp/INDEX.md) - Arquitetura MVP
3. [QUICK_START.md](./mvp/QUICK_START.md) - Como começar

### Correção de Problemas
1. [code-review/INDEX.md](./code-review/INDEX.md) - Resultados do code review
2. [code-review/guides/](./code-review/guides/) - Guias de correção
3. Code Issues Panel no IDE - Findings detalhados

### DevOps
1. [AWS_EC2_SPOT_SETUP.md](./AWS_EC2_SPOT_SETUP.md)
2. [DEPLOY_CHECKLIST.md](./DEPLOY_CHECKLIST.md)
3. [code-review/INFRASTRUCTURE.md](./code-review/INFRASTRUCTURE.md)

### Security Team
1. [code-review/SECURITY_ISSUES.md](./code-review/SECURITY_ISSUES.md)
2. [LOGIN_SECURITY.md](./LOGIN_SECURITY.md)
3. [RECORDING_SECURITY.md](./RECORDING_SECURITY.md)

## 📝 Convenções

### Nomenclatura
- `INDEX.md` - Índice de uma seção
- `README.md` - Introdução/overview
- `*_SETUP.md` - Guias de configuração
- `*_CHECKLIST.md` - Checklists
- `FIX_*.md` - Guias de correção

### Estrutura de Documentos
```markdown
# Título

## Resumo
Breve descrição do documento

## Problema
Descrição do problema

## Solução
Como resolver

## Exemplos
Código de exemplo

## Checklist
- [ ] Item 1
- [ ] Item 2

## Referências
Links úteis
```

## 🔄 Manutenção

### Atualizar Documentação
1. Manter docs sincronizados com código
2. Atualizar após mudanças de arquitetura
3. Revisar mensalmente

### Adicionar Novo Documento
1. Seguir convenções de nomenclatura
2. Adicionar ao índice apropriado
3. Linkar de documentos relacionados

## 📞 Suporte

Dúvidas sobre documentação:
- Consulte o índice apropriado
- Verifique documentos relacionados
- Consulte o Code Issues Panel para findings
