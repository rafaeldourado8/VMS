# 📊 GT-Vision Architecture Diagrams

Diagramas da arquitetura, CI/CD e estratégias de deploy do GT-Vision VMS.

## 📁 Arquivos

1. **01-cicd-flow.excalidraw** - Fluxo completo de CI/CD
2. **02-aws-architecture.excalidraw** - Arquitetura AWS (Dev, Staging, Production)
3. **03-blue-green-deployment.excalidraw** - Estratégia Blue/Green Deploy
4. **04-chaos-engineering.excalidraw** - Chaos Monkey e testes de resiliência
5. **05-monitoring-observability.excalidraw** - Stack de monitoramento

## 🎨 Como Visualizar

### Opção 1: Excalidraw Online (Recomendado)
1. Acesse https://excalidraw.com
2. Clique em "Open" no menu
3. Selecione o arquivo `.excalidraw` desejado
4. Visualize e edite online

### Opção 2: VS Code Extension
1. Instale a extensão "Excalidraw" no VS Code
2. Abra o arquivo `.excalidraw`
3. Visualize diretamente no editor

### Opção 3: Excalidraw Desktop
1. Baixe em https://github.com/excalidraw/excalidraw-desktop
2. Instale o aplicativo
3. Abra os arquivos `.excalidraw`

## 📝 Descrição dos Diagramas

### 1. CI/CD Flow
Mostra o fluxo completo desde o `git push` até o deploy em produção:
- Pipeline de CI (develop branch)
- Testes automatizados
- Deploy em Dev Server
- Pipeline de CD (main branch)
- Chaos Engineering
- Blue/Green deployment

### 2. AWS Architecture
Arquitetura completa dos 3 ambientes:
- **Dev**: EC2 Spot + Docker Compose ($50/mês)
- **Staging**: Clone de produção ($100/mês)
- **Production**: Blue/Green + RDS + S3 ($600/mês)

### 3. Blue/Green Deployment
Estratégia de deploy sem downtime:
- 6 etapas do deploy
- Switch gradual de tráfego (10% → 50% → 100%)
- Rollback automático
- Métricas monitoradas

### 4. Chaos Engineering
Testes de resiliência do sistema:
- Kill containers aleatórios
- Network chaos (latência, packet loss)
- CPU/Disk stress
- Health checks e recovery

### 5. Monitoring & Observability
Stack completo de monitoramento:
- Prometheus (métricas)
- Loki (logs)
- Grafana (visualização)
- Alert Manager (alertas)
- Integrações (Slack, Email, PagerDuty)

## 🎯 Uso

Estes diagramas devem ser usados para:
- ✅ Documentação técnica
- ✅ Onboarding de novos desenvolvedores
- ✅ Apresentações para stakeholders
- ✅ Planejamento de infraestrutura
- ✅ Troubleshooting e incident response

## 🔄 Atualizações

Mantenha os diagramas atualizados quando:
- Adicionar novos serviços
- Mudar estratégia de deploy
- Alterar arquitetura AWS
- Implementar novos testes
- Modificar stack de monitoramento

## 📚 Referências

- [Excalidraw Documentation](https://docs.excalidraw.com)
- [AWS Architecture Center](https://aws.amazon.com/architecture)
- [Blue/Green Deployments](https://docs.aws.amazon.com/whitepapers/latest/blue-green-deployments/welcome.html)
- [Chaos Engineering Principles](https://principlesofchaos.org)
- [Prometheus Best Practices](https://prometheus.io/docs/practices)

---

**Última atualização**: 2025-02-09
**Mantido por**: GT-Vision DevOps Team
