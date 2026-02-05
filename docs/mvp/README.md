# 📹 GTVISION MVP - GRAVAÇÃO 24/7

## VISÃO GERAL

O GTVision é um sistema VMS (Video Management System) profissional que combina:
- **Live Streaming** via MediaMTX (RTSP/RTMP → HLS)
- **Gravação Contínua 24/7** em fMP4
- **Playback** de gravações via HLS (reutilizando player existente)
- **LPR (License Plate Recognition)** em tempo real e offline
- **Arquitetura Multi-Tenant** com isolamento por tenant_id

---

## ESTADO ATUAL DO PROJETO

### ✅ O QUE JÁ FUNCIONA

#### 1. Live Streaming (PRODUÇÃO)
- MediaMTX configurado e estável
- Player web consumindo HLS
- Provisionamento dinâmico de câmeras via API
- Suporte a 12 câmeras simultâneas por nó MediaMTX
- HLS otimizado: 6 segmentos × 4s = 24s buffer

#### 2. Backend (Django)
- API REST completa
- Gerenciamento de câmeras, usuários, tenants
- Integração com PostgreSQL
- Redis para cache
- Apps: cameras, analytics, clips, deteccoes, onvif

#### 3. Frontend (React + Vite)
- Player HLS funcional e validado
- Dashboard de câmeras
- Timeline (estrutura pronta)
- Interface multi-tenant

#### 4. Infraestrutura
- Docker Compose funcional
- HAProxy para load balancing
- Kong API Gateway
- Nginx para arquivos estáticos
- Redis + PostgreSQL

#### 5. Serviços Auxiliares
- **Streaming Service** (FastAPI): Provisiona câmeras no MediaMTX
- **ONVIF Service**: Descoberta e controle PTZ
- **Clips Service**: Geração de clipes sob demanda
- **Storage Service**: Indexação de gravações

---

## ❌ O QUE FALTA IMPLEMENTAR

### 1. Gravação 24/7 (CORE DO MVP)
- ✅ Configuração MediaMTX ajustada
- ⏳ Validação de gravação contínua
- ⏳ Testes de retenção cíclica (7 dias)
- ⏳ Monitoramento de disco

### 2. Playback de Gravações
- ⏳ Serviço de Playback (FastAPI)
- ⏳ API de Timeline
- ⏳ Integração com player existente
- ⏳ Busca por data/hora

### 3. Escala Multi-Nó
- ⏳ Orquestração de múltiplos MediaMTX
- ⏳ Balanceamento de câmeras por nó
- ⏳ Health check e failover
- ⏳ Migração de câmeras entre nós

### 4. Deploy Cloud (AWS)
- ⏳ Terraform para EC2 + EBS
- ⏳ Auto-scaling de nós MediaMTX
- ⏳ Backup de gravações para S3
- ⏳ CloudWatch monitoring

### 5. CI/CD
- ⏳ GitHub Actions pipeline
- ⏳ Testes automatizados
- ⏳ Deploy staging/produção
- ⏳ Rollback automático

---

## CAPACIDADE ATUAL

### Por Nó MediaMTX
- **Câmeras simultâneas**: 10-15 (recomendado: 12)
- **Bitrate médio por câmera**: 2-4 Mbps
- **Throughput total**: ~50 Mbps
- **CPU**: 2.5 cores (limite Docker)
- **RAM**: 2GB (limite Docker)
- **Disco**: Depende da retenção

### Cálculo de Disco (7 dias de retenção)

```
1 câmera × 3 Mbps × 3600s × 24h × 7 dias = ~226 GB/câmera/semana
12 câmeras = ~2.7 TB por nó
```

### Para 120 Câmeras (MVP)
- **Nós MediaMTX necessários**: 10 nós (12 câmeras cada)
- **Disco total**: ~27 TB (EBS gp3 ou local SSD)
- **Custo AWS estimado**: 
  - 10× EC2 t3.large: ~$730/mês
  - 27TB EBS gp3: ~$2,430/mês
  - **Total**: ~$3,160/mês

---

## ARQUITETURA DE GRAVAÇÃO

### Fluxo de Dados

```
┌─────────┐
│ Câmera  │ RTSP
│ IP      │────────┐
└─────────┘        │
                   ▼
              ┌──────────┐
              │ MediaMTX │
              │  (Nó 1)  │
              └──────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
    [Gravação]  [HLS]    [Playback]
        │          │          │
        ▼          ▼          ▼
    /recordings  Player   Timeline
    cam_1/       (Live)   (Histórico)
    └─2026-02-05/
      ├─00.mp4
      ├─01.mp4
      └─...
```

### Estrutura de Arquivos

```
/recordings/
├── cam_1/
│   ├── 2026-02-05/
│   │   ├── 00.mp4  (00:00-00:59)
│   │   ├── 01.mp4  (01:00-01:59)
│   │   ├── 02.mp4  (02:00-02:59)
│   │   └── ... (24 arquivos/dia)
│   └── 2026-02-06/
│       └── ...
├── cam_2/
│   └── ...
```

**Padrão**: `/recordings/{camera_id}/{YYYY-MM-DD}/{HH}.mp4`

---

## CONFIGURAÇÃO MEDIAMTX (FINAL)

```yaml
pathDefaults:
  record: yes
  recordPath: /recordings/%path/%Y-%m-%d/%H.mp4
  recordFormat: fmp4
  recordPartDuration: 2s
  recordSegmentDuration: 1h
  recordDeleteAfter: 168h
```

### Parâmetros Críticos

| Parâmetro | Valor | Motivo |
|-----------|-------|--------|
| `recordFormat` | `fmp4` | Fragmentado, recuperável, compatível HLS |
| `recordPartDuration` | `2s` | Fragmentos pequenos para baixa latência |
| `recordSegmentDuration` | `1h` | 1 arquivo por hora (padrão VMS) |
| `recordDeleteAfter` | `168h` | 7 dias de retenção cíclica |

---

## PLAYBACK SEM ALTERAR O PLAYER

### Estratégia

O player atual consome HLS. Para playback de gravações:

1. **Backend recebe requisição**: `GET /playback?camera_id=1&start=2026-02-05T15:30:00`
2. **Backend identifica arquivo**: `/recordings/cam_1/2026-02-05/15.mp4`
3. **Backend cria path temporário no MediaMTX**:
   ```json
   {
     "source": "file:///recordings/cam_1/2026-02-05/15.mp4",
     "sourceOnDemand": true
   }
   ```
4. **MediaMTX remux MP4 → HLS** sob demanda
5. **Player consome HLS** (não sabe que é gravação)

### Vantagens
- ✅ Player não muda
- ✅ Mesma infraestrutura (MediaMTX)
- ✅ Sem transcodificação
- ✅ Seek funciona nativamente

---

## RISCOS E MITIGAÇÕES

### 1. Disco Cheio
**Risco**: Gravação para se disco encher antes de 7 dias.

**Mitigação**:
- MediaMTX apaga automaticamente (`recordDeleteAfter`)
- Monitoramento de disco (alerta < 20%)
- Alarme CloudWatch (AWS)

### 2. Falha de Rede
**Risco**: Câmera offline = buraco na gravação.

**Mitigação**:
- MediaMTX reconecta automaticamente
- Logs de desconexão
- Alerta de câmera offline > 5min

### 3. Restart do MediaMTX
**Risco**: Perda de gravação durante restart.

**Mitigação**:
- Gravação é por arquivo (não buffer)
- Último arquivo pode ficar incompleto
- Validação de integridade (ffprobe)

### 4. Corrupção de Arquivo
**Risco**: Arquivo MP4 corrompido.

**Mitigação**:
- fMP4 é recuperável (headers distribuídos)
- Validação periódica (cron)
- Backup crítico para S3

### 5. Escala (120 câmeras)
**Risco**: Um único MediaMTX não aguenta.

**Mitigação**:
- Arquitetura multi-nó (10 nós × 12 câmeras)
- Backend decide alocação
- Health check e redistribuição

---

## TESTES OBRIGATÓRIOS

### Checklist de Gravação

- [ ] Gravação contínua por 24h
- [ ] Arquivos de 1h criados corretamente
- [ ] Estrutura de pastas correta
- [ ] Retenção de 7 dias funciona
- [ ] Restart do MediaMTX não corrompe arquivo
- [ ] Câmera offline → reconexão automática
- [ ] Disco cheio → arquivos antigos apagados
- [ ] 12 câmeras simultâneas sem perda

### Checklist de Playback

- [ ] Timeline retorna segmentos corretos
- [ ] Playback inicia em < 2s
- [ ] Seek funciona
- [ ] Player não percebe diferença (live vs gravação)
- [ ] Múltiplos playbacks simultâneos
- [ ] Playback de arquivo de 7 dias atrás

### Checklist de Escala

- [ ] 10 nós MediaMTX simultâneos
- [ ] 120 câmeras gravando
- [ ] Balanceamento de carga
- [ ] Failover de nó
- [ ] Migração de câmera entre nós

---

## PRÓXIMOS PASSOS

Consulte a pasta `sprints/` para o planejamento detalhado das 20 sprints.

**Sprint 1-5**: Gravação e Playback  
**Sprint 6-10**: Escala Multi-Nó  
**Sprint 11-15**: Deploy Cloud (AWS)  
**Sprint 16-20**: Otimizações e Produção
