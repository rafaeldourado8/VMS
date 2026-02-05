# 📚 DOCUMENTAÇÃO GTVISION MVP - ÍNDICE

## ESTRUTURA DA DOCUMENTAÇÃO

```
docs/mvp/
├── README.md                    # Visão geral e estado atual
├── RESUMO_EXECUTIVO.md          # Resumo para stakeholders
├── ARQUITETURA_TECNICA.md       # Detalhes técnicos profundos
├── CHECKLIST_TESTES.md          # Todos os testes necessários
├── RISCOS_MITIGACOES.md         # Riscos e como mitigá-los
├── INDEX.md                     # Este arquivo
└── sprints/
    ├── README.md                # Visão geral das 20 sprints
    ├── SPRINT_01.md             # Validação de gravação
    ├── SPRINT_02.md             # Retenção cíclica
    ├── SPRINT_03.md             # Serviço de playback
    ├── SPRINT_04_10.md          # Integração e escala
    ├── SPRINT_11_15.md          # Deploy AWS
    └── SPRINT_16_20.md          # CI/CD e produção
```

---

## GUIA DE LEITURA

### Para Stakeholders / Product Owners
1. **[RESUMO_EXECUTIVO.md](RESUMO_EXECUTIVO.md)** - Visão geral, custos, cronograma
2. **[sprints/README.md](sprints/README.md)** - Planejamento das 20 sprints
3. **[RISCOS_MITIGACOES.md](RISCOS_MITIGACOES.md)** - Riscos principais

### Para Engenheiros Backend
1. **[README.md](README.md)** - Estado atual do projeto
2. **[ARQUITETURA_TECNICA.md](ARQUITETURA_TECNICA.md)** - Arquitetura detalhada
3. **[sprints/SPRINT_03.md](sprints/SPRINT_03.md)** - Implementação do serviço de playback
4. **[sprints/SPRINT_04_10.md](sprints/SPRINT_04_10.md)** - Orquestração multi-nó

### Para Engenheiros DevOps
1. **[ARQUITETURA_TECNICA.md](ARQUITETURA_TECNICA.md)** - Seção "Deploy: Local vs Cloud"
2. **[sprints/SPRINT_11_15.md](sprints/SPRINT_11_15.md)** - Terraform e AWS
3. **[sprints/SPRINT_16_20.md](sprints/SPRINT_16_20.md)** - CI/CD e monitoramento
4. **[RISCOS_MITIGACOES.md](RISCOS_MITIGACOES.md)** - Planos de contingência

### Para Engenheiros Frontend
1. **[README.md](README.md)** - Seção "Playback sem alterar o player"
2. **[sprints/SPRINT_04_10.md](sprints/SPRINT_04_10.md)** - Sprint 4: Integração frontend
3. **[ARQUITETURA_TECNICA.md](ARQUITETURA_TECNICA.md)** - Seção "Playback: Arquitetura Detalhada"

### Para QA Engineers
1. **[CHECKLIST_TESTES.md](CHECKLIST_TESTES.md)** - Todos os testes necessários
2. **[sprints/SPRINT_01.md](sprints/SPRINT_01.md)** - Testes de gravação
3. **[sprints/SPRINT_05.md](sprints/SPRINT_04_10.md#sprint-5)** - Testes de estresse

---

## DOCUMENTOS POR TÓPICO

### Gravação 24/7
- [README.md](README.md) - Seção "Arquitetura de Gravação"
- [ARQUITETURA_TECNICA.md](ARQUITETURA_TECNICA.md) - Seção "Fluxo de Gravação Detalhado"
- [sprints/SPRINT_01.md](sprints/SPRINT_01.md) - Validação de gravação
- [sprints/SPRINT_02.md](sprints/SPRINT_02.md) - Retenção cíclica

### Playback
- [README.md](README.md) - Seção "Playback sem alterar o player"
- [ARQUITETURA_TECNICA.md](ARQUITETURA_TECNICA.md) - Seção "Playback: Arquitetura Detalhada"
- [sprints/SPRINT_03.md](sprints/SPRINT_03.md) - Implementação do serviço

### Escala Multi-Nó
- [README.md](README.md) - Seção "Capacidade Atual"
- [ARQUITETURA_TECNICA.md](ARQUITETURA_TECNICA.md) - Seção "Escala: Arquitetura Multi-Nó"
- [sprints/SPRINT_04_10.md](sprints/SPRINT_04_10.md) - Sprints 6-10

### Deploy AWS
- [ARQUITETURA_TECNICA.md](ARQUITETURA_TECNICA.md) - Seção "Deploy: Local vs Cloud"
- [sprints/SPRINT_11_15.md](sprints/SPRINT_11_15.md) - Terraform e CloudWatch
- [RESUMO_EXECUTIVO.md](RESUMO_EXECUTIVO.md) - Seção "Custos"

### CI/CD
- [sprints/SPRINT_16_20.md](sprints/SPRINT_16_20.md) - Sprints 16-17
- [RISCOS_MITIGACOES.md](RISCOS_MITIGACOES.md) - Seção "Bugs em Produção"

### Segurança
- [sprints/SPRINT_16_20.md](sprints/SPRINT_16_20.md) - Sprint 19
- [RISCOS_MITIGACOES.md](RISCOS_MITIGACOES.md) - Seção "Acesso Não Autorizado"

### Testes
- [CHECKLIST_TESTES.md](CHECKLIST_TESTES.md) - Checklist completo
- [sprints/SPRINT_01.md](sprints/SPRINT_01.md) - Testes de gravação
- [sprints/SPRINT_04_10.md](sprints/SPRINT_04_10.md) - Sprint 5: Testes de estresse

### Riscos
- [RISCOS_MITIGACOES.md](RISCOS_MITIGACOES.md) - Documento completo
- [RESUMO_EXECUTIVO.md](RESUMO_EXECUTIVO.md) - Seção "Riscos Principais"

---

## QUICK START

### 1. Entender o Projeto (15 minutos)
```bash
# Ler resumo executivo
cat docs/mvp/RESUMO_EXECUTIVO.md

# Ver estado atual
cat docs/mvp/README.md | grep "ESTADO ATUAL" -A 20
```

### 2. Configurar Ambiente (30 minutos)
```bash
# Verificar configuração MediaMTX
cat mediamtx.yml | grep -A 10 "pathDefaults"

# Subir ambiente
docker-compose up -d

# Verificar saúde
docker ps
curl http://localhost:9997/v3/config/global/get
```

### 3. Executar Sprint 1 (1 semana)
```bash
# Seguir instruções em:
cat docs/mvp/sprints/SPRINT_01.md
```

---

## COMANDOS ÚTEIS

### Verificar Gravação
```bash
# Listar gravações
ls -lh /recordings/cam_*/$(date +%Y-%m-%d)/

# Validar arquivo
ffprobe /recordings/cam_1/$(date +%Y-%m-%d)/$(date +%H).mp4

# Monitorar em tempo real
watch -n 60 'du -sh /recordings/cam_*'
```

### Verificar Saúde do Sistema
```bash
# MediaMTX
curl http://localhost:9997/v3/paths/list | jq

# Streaming Service
curl http://localhost:8001/stats | jq

# Backend
curl http://localhost:8000/admin/login/
```

### Logs
```bash
# MediaMTX
docker logs -f gtvision_mediamtx

# Streaming
docker logs -f gtvision_streaming

# Backend
docker logs -f gtvision_backend
```

---

## GLOSSÁRIO

| Termo | Significado |
|-------|-------------|
| **VMS** | Video Management System |
| **fMP4** | Fragmented MP4 (formato de gravação) |
| **HLS** | HTTP Live Streaming (formato de streaming) |
| **RTSP** | Real Time Streaming Protocol (protocolo de câmeras) |
| **MediaMTX** | Servidor de streaming open-source |
| **Nó** | Instância do MediaMTX (suporta 12 câmeras) |
| **Retenção** | Tempo que gravações são mantidas (7 dias) |
| **Playback** | Reprodução de gravações antigas |
| **Timeline** | Linha do tempo de gravações disponíveis |
| **Failover** | Recuperação automática de falhas |
| **Blue-Green** | Estratégia de deploy sem downtime |

---

## PERGUNTAS FREQUENTES

### Por que fMP4 e não TS?
fMP4 tem menor overhead, é mais fácil de indexar e é o padrão moderno para HLS. Ver [ARQUITETURA_TECNICA.md](ARQUITETURA_TECNICA.md#por-que-fmp4).

### Por que 1 hora por arquivo?
É o padrão da indústria VMS. Facilita busca e é um bom balanço entre granularidade e número de arquivos. Ver [ARQUITETURA_TECNICA.md](ARQUITETURA_TECNICA.md#por-que-1-hora-por-arquivo).

### Por que não gravar HLS?
HLS é formato de streaming, não de armazenamento. Gera milhares de arquivos pequenos e tem overhead alto. Ver [ARQUITETURA_TECNICA.md](ARQUITETURA_TECNICA.md#por-que-não-gravar-hls).

### Como funciona o playback sem alterar o player?
MediaMTX lê o MP4 gravado e remux para HLS sob demanda. O player não sabe que é gravação. Ver [README.md](README.md#playback-sem-alterar-o-player).

### Por que 10 nós para 120 câmeras?
Cada nó suporta 12 câmeras (limite de CPU). 120 / 12 = 10 nós. Ver [README.md](README.md#capacidade-atual).

### Quanto custa rodar 120 câmeras na AWS?
~$2,500/mês com otimizações (Reserved Instances, gp3, etc). Ver [RESUMO_EXECUTIVO.md](RESUMO_EXECUTIVO.md#custos).

### O que acontece se o disco encher?
MediaMTX apaga arquivos antigos automaticamente (recordDeleteAfter: 168h). Ver [RISCOS_MITIGACOES.md](RISCOS_MITIGACOES.md#disco-cheio).

### Como fazer rollback se houver bug?
Deploy blue-green permite rollback em < 5 minutos. Ver [sprints/SPRINT_16_20.md](sprints/SPRINT_16_20.md#sprint-17).

---

## CONTRIBUINDO

### Atualizar Documentação
```bash
# Editar arquivo
vim docs/mvp/README.md

# Commit
git add docs/mvp/
git commit -m "docs: atualizar README com nova feature"
git push
```

### Adicionar Nova Sprint
```bash
# Criar arquivo
vim docs/mvp/sprints/SPRINT_21.md

# Seguir template de SPRINT_01.md
```

---

## CHANGELOG

### 2026-02-05 - v1.0
- ✅ Documentação inicial completa
- ✅ 20 sprints planejadas
- ✅ Configuração MediaMTX ajustada
- ✅ Checklist de testes criado
- ✅ Riscos mapeados e mitigados

---

## CONTATO

**Dúvidas sobre a documentação?**
- Abra uma issue no GitHub
- Envie email para: tech@gtvision.com
- Slack: #gtvision-dev

---

**Última atualização**: 2026-02-05  
**Versão**: 1.0  
**Mantenedor**: Equipe GTVision
