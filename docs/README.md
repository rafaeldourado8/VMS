# 📚 DOCUMENTAÇÃO GTVISION

## ESTRUTURA

```
docs/
├── mvp/                          # ⭐ DOCUMENTAÇÃO DO MVP (NOVO)
│   ├── QUICK_START.md            # 🚀 Comece aqui (5 minutos)
│   ├── README.md                 # Visão geral do MVP
│   ├── RESUMO_EXECUTIVO.md       # Para stakeholders
│   ├── ARQUITETURA_TECNICA.md    # Detalhes técnicos
│   ├── CHECKLIST_TESTES.md       # Todos os testes
│   ├── RISCOS_MITIGACOES.md      # Riscos e soluções
│   ├── INDEX.md                  # Índice completo
│   └── sprints/                  # 20 sprints detalhadas
│       ├── README.md
│       ├── SPRINT_01.md
│       ├── SPRINT_02.md
│       ├── SPRINT_03.md
│       ├── SPRINT_04_10.md
│       ├── SPRINT_11_15.md
│       └── SPRINT_16_20.md
│
├── alpr/                         # Documentação LPR
├── analytics/                    # Documentação Analytics
├── clips/                        # Documentação Clips
└── day_0/                        # Documentação inicial

```

---

## 🚀 COMECE AQUI

### Você quer implementar gravação 24/7?
👉 **[mvp/QUICK_START.md](mvp/QUICK_START.md)** - 5 minutos para começar

### Você é stakeholder/PM?
👉 **[mvp/RESUMO_EXECUTIVO.md](mvp/RESUMO_EXECUTIVO.md)** - Visão geral, custos, cronograma

### Você é engenheiro?
👉 **[mvp/README.md](mvp/README.md)** - Estado atual e capacidades  
👉 **[mvp/ARQUITETURA_TECNICA.md](mvp/ARQUITETURA_TECNICA.md)** - Detalhes técnicos

### Você precisa testar?
👉 **[mvp/CHECKLIST_TESTES.md](mvp/CHECKLIST_TESTES.md)** - Todos os testes

### Você quer ver o planejamento?
👉 **[mvp/sprints/README.md](mvp/sprints/README.md)** - 20 sprints (4 meses)

---

## 📖 DOCUMENTAÇÃO POR ÁREA

### Gravação 24/7 (MVP)
- **[mvp/](mvp/)** - Documentação completa do MVP
- **Status**: ✅ Configuração pronta, aguardando validação
- **Próximo passo**: Sprint 1 (validação de gravação)

### LPR (License Plate Recognition)
- **[alpr/](alpr/)** - Documentação do sistema de reconhecimento de placas
- **Status**: ✅ Funcionando em produção

### Analytics
- **[analytics/](analytics/)** - Documentação de analytics e métricas
- **Status**: ✅ Funcionando

### Clips
- **[clips/](clips/)** - Documentação de geração de clipes
- **Status**: ✅ Funcionando

### Day 0
- **[day_0/](day_0/)** - Documentação inicial do projeto
- **Status**: 📚 Referência histórica

---

## 🎯 OBJETIVOS DO MVP

1. **Gravação contínua 24/7** de 120 câmeras
2. **Retenção de 7 dias** com deleção automática
3. **Playback** via HLS (sem alterar player)
4. **Escala multi-nó** (10 nós × 12 câmeras)
5. **Deploy AWS** com Terraform
6. **CI/CD** completo

**Prazo**: 4 meses (20 sprints)  
**Custo**: ~$2,500/mês (AWS otimizado)

---

## 📊 STATUS ATUAL

### ✅ Implementado
- Live streaming (MediaMTX + HLS)
- Player web (React + HLS.js)
- Backend (Django + FastAPI)
- Provisionamento dinâmico de câmeras
- LPR em tempo real

### ⏳ Em Implementação
- **Gravação 24/7** (configuração pronta)
- Playback de gravações
- Escala multi-nó
- Deploy AWS
- CI/CD

---

## 🔗 LINKS RÁPIDOS

| Documento | Descrição | Tempo de Leitura |
|-----------|-----------|------------------|
| [QUICK_START.md](mvp/QUICK_START.md) | Comece agora | 5 min |
| [RESUMO_EXECUTIVO.md](mvp/RESUMO_EXECUTIVO.md) | Visão geral | 10 min |
| [README.md](mvp/README.md) | Estado atual | 15 min |
| [ARQUITETURA_TECNICA.md](mvp/ARQUITETURA_TECNICA.md) | Detalhes técnicos | 30 min |
| [CHECKLIST_TESTES.md](mvp/CHECKLIST_TESTES.md) | Todos os testes | 20 min |
| [RISCOS_MITIGACOES.md](mvp/RISCOS_MITIGACOES.md) | Riscos e soluções | 25 min |
| [sprints/README.md](mvp/sprints/README.md) | Planejamento | 15 min |

---

## 💡 DICAS

### Primeira vez no projeto?
1. Leia [mvp/QUICK_START.md](mvp/QUICK_START.md)
2. Execute os comandos
3. Valide a gravação
4. Leia [mvp/README.md](mvp/README.md)

### Precisa implementar algo?
1. Veja [mvp/sprints/README.md](mvp/sprints/README.md)
2. Escolha a sprint relevante
3. Siga o passo a passo

### Encontrou um problema?
1. Consulte [mvp/RISCOS_MITIGACOES.md](mvp/RISCOS_MITIGACOES.md)
2. Veja a seção de troubleshooting
3. Execute os comandos de debug

---

## 📞 CONTATO

**Dúvidas sobre documentação?**
- GitHub Issues
- Email: tech@gtvision.com
- Slack: #gtvision-dev

---

**Última atualização**: 2026-02-05  
**Versão**: 1.0
