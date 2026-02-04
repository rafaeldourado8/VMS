# Day 0 - Decisões Técnicas

## 1. Gravação Contínua vs Motion Detection

### Decisão: Gravação Contínua 24/7

**Razões**:
- ✅ Simplicidade operacional (sem configuração de sensibilidade)
- ✅ Zero perda de eventos (não depende de algoritmo de detecção)
- ✅ Reprocessamento offline (ALPR, Analytics podem rodar depois)
- ✅ Confiabilidade (sem falsos negativos)

**Trade-offs**:
- ❌ Storage maior (~1.7TB para 12 câmeras, 7 dias)
- ❌ Processamento contínuo de FFmpeg

**Alternativa rejeitada**: Motion detection
- Complexidade de configuração
- Risco de perder eventos importantes
- Dificuldade de tuning para diferentes cenários

---

## 2. Dual-Path Recording Architecture

### Decisão: MediaMTX (streaming) + Recorder Service (storage)

**Arquitetura**:
```
Camera RTSP → MediaMTX (5Mbps) → Frontend (HLS)
                  ↓
            Recorder Service (2Mbps) → Storage
```

**Razões**:
- ✅ Streaming em alta qualidade (5Mbps) para visualização
- ✅ Storage otimizado (2Mbps) para ALPR/Analytics
- ✅ Desacoplamento (falha no recorder não afeta streaming)
- ✅ Flexibilidade (diferentes codecs/bitrates por uso)

**Alternativa rejeitada**: MediaMTX recording nativo
- Não permite bitrate diferente para storage
- Menos controle sobre segmentação
- Dificulta implementação de políticas de retenção customizadas

---

## 3. Snapshot Estático vs Polling

### Decisão: Snapshot estático com localStorage

**Implementação**:
- Fetch único na montagem do componente
- Cache em localStorage (chave: `camera_snapshot_{id}`)
- Status indicator baseado em `camera.status` do backend

**Razões**:
- ✅ Redução de 99% na banda (2KB/s → 20KB one-time)
- ✅ Melhor UX (carregamento instantâneo após primeira visita)
- ✅ Menos carga no servidor

**Alternativa rejeitada**: Polling contínuo
- Banda desnecessária para imagem que muda pouco
- Carga excessiva no servidor com muitas câmeras
- Não agrega valor (thumbnail não precisa ser real-time)

---

## 4. List View Only (sem Grid)

### Decisão: Remover grid view, manter apenas lista

**Razões**:
- ✅ Melhor escalabilidade (12+ câmeras)
- ✅ Mais informações visíveis (status, IP, localização)
- ✅ Paginação mais natural
- ✅ Menos código para manter

**Alternativa rejeitada**: Grid + List toggle
- Grid não escala bem (>12 câmeras fica confuso)
- Toggle adiciona complexidade desnecessária
- Usuário prefere lista para gerenciamento

---

## 5. FFmpeg CRF 28 para Storage

### Decisão: CRF 28 (qualidade média-baixa)

**Razões**:
- ✅ Suficiente para ALPR (placas legíveis)
- ✅ Redução significativa de storage (59%)
- ✅ Menor uso de CPU (preset veryfast)

**Testes**:
| CRF | Qualidade | Tamanho | Uso CPU |
|-----|-----------|---------|---------|
| 18  | Excelente | 100%    | Alto    |
| 23  | Boa       | 60%     | Médio   |
| 28  | Média     | 40%     | Baixo   |

**Alternativa rejeitada**: CRF 18 (alta qualidade)
- Storage 2.5x maior
- Desnecessário para processamento offline
- Maior uso de CPU

---

## 6. Segmentação Diária (86400s)

### Decisão: 1 arquivo por dia por câmera

**Razões**:
- ✅ Facilita organização (1 arquivo = 1 dia)
- ✅ Simplifica limpeza (delete por data)
- ✅ Reduz fragmentação de arquivos

**Alternativa rejeitada**: Segmentos de 1h
- 24 arquivos por dia por câmera
- Mais complexo para buscar eventos
- Maior overhead de I/O

---

## 7. Clips Service Separado

### Decisão: Microserviço dedicado para extração de clips

**Razões**:
- ✅ Isolamento de processamento pesado (FFmpeg)
- ✅ Escalabilidade independente
- ✅ Não impacta backend Django

**Alternativa rejeitada**: Clips no backend Django
- FFmpeg bloquearia workers do Django
- Dificulta escalabilidade horizontal
- Mistura responsabilidades

---

## 8. Redis Cache para Snapshots

### Decisão: Cache de 24h no Redis

**Razões**:
- ✅ Evita re-captura desnecessária
- ✅ Resposta instantânea
- ✅ TTL automático (24h)

**Alternativa rejeitada**: Sem cache
- Cada requisição executaria FFmpeg
- Carga excessiva no MediaMTX
- Latência alta

---

## 9. Recorder Error Handling

### Decisão: Graceful degradation com logs

**Implementação**:
```python
if resp.status_code == 401:
    logger.error("❌ Não autorizado")
    return

if not isinstance(cameras, list):
    logger.error("❌ Resposta inválida")
    return
```

**Razões**:
- ✅ Não crashar o serviço
- ✅ Logs claros para debug
- ✅ Permite deploy mesmo com auth pendente

**Alternativa rejeitada**: Crash on error
- Dificulta desenvolvimento
- Requer auth implementado antes de testar

---

## 10. Retenção de 7 Dias

### Decisão: 168h de retenção

**Razões**:
- ✅ Balanceamento storage vs histórico
- ✅ Suficiente para investigações
- ✅ Compatível com storage disponível

**Cálculo**:
- 12 câmeras × 7 dias = 1.7TB
- Storage disponível: 2-4TB (margem confortável)

**Alternativa rejeitada**: 30 dias
- 7.3TB necessário
- Custo de storage muito alto
- Maioria dos eventos investigados em <7 dias

---

## Métricas de Sucesso

| Métrica | Antes | Depois | Melhoria |
|---------|-------|--------|----------|
| Banda/câmera | 2KB/s | 20KB one-time | 99% ↓ |
| Storage/12cam/7d | 4.15TB | 1.7TB | 59% ↓ |
| Arquivos/dia/cam | N/A | 1 | Organização |
| Latência snapshot | N/A | <100ms (cache) | Instantâneo |

---

## Lições Aprendidas

1. **Desacoplamento é chave**: Streaming e Storage separados permite otimização independente
2. **Cache agressivo**: Snapshots não precisam ser real-time
3. **Simplicidade > Features**: Gravação contínua é mais confiável que motion detection
4. **Storage é barato**: 1.7TB é aceitável para 12 câmeras profissionais
5. **Microserviços para processamento pesado**: FFmpeg não deve rodar no backend principal

---

## Débitos Técnicos

1. **Auth service-to-service**: Recorder precisa autenticar com backend
2. **Health checks**: Recorder deve reportar status ao backend
3. **Retry logic**: Reconexão automática em caso de falha de stream
4. **Monitoring**: Dashboard de storage e performance
5. **Testes de carga**: Validar com 12+ câmeras simultâneas
