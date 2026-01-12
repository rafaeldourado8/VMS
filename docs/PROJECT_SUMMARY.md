# 📋 VMS - RESUMO COMPLETO DO PROJETO

## 🎯 VISÃO GERAL

Sistema de monitoramento de vídeo com IA para detecção de placas veiculares (LPR) e busca retroativa em gravações.

---

## 🏗️ ARQUITETURA ATUAL

### Componentes Implementados ✅

#### 1. MediaMTX (Streaming)
- **Função**: Streaming HLS/WebRTC + Gravação contínua
- **Status**: ✅ Funcionando
- **Portas**: 8888 (HLS), 8889 (WebRTC), 9997 (API)

#### 2. Backend (Django)
- **Função**: API REST, gerenciamento de câmeras, usuários
- **Status**: ✅ Funcionando
- **Porta**: 8000

#### 3. Frontend (React + Vite)
- **Função**: Interface web
- **Status**: ✅ Funcionando
- **Porta**: 5173

#### 4. LPR Detection (YOLO + OCR)
- **Função**: Detecção de placas em câmeras RTSP
- **Status**: ✅ Integrado
- **Porta**: 5000
- **Modelo**: YOLOv8n + Fast-Plate-OCR

#### 5. PostgreSQL
- **Função**: Banco de dados principal
- **Status**: ✅ Funcionando

#### 6. Redis
- **Função**: Cache
- **Status**: ✅ Funcionando

#### 7. RabbitMQ
- **Função**: Mensageria
- **Status**: ✅ Funcionando

#### 8. Prometheus
- **Função**: Monitoramento
- **Status**: ✅ Funcionando
- **Porta**: 9090

---

## 📹 TIPOS DE CÂMERAS

### RTSP (LPR) - Alta Definição
```
Protocolo: rtsp://
Quantidade: 10-20 por cidade
IA: ATIVA (YOLO + OCR)
Função: Detecção de placas em tempo real
Gravação: SIM (contínua)
```

### RTMP (Bullets) - Padrão
```
Protocolo: rtmp://
Quantidade: até 1000 por cidade
IA: DESATIVADA
Função: Apenas monitoramento
Gravação: SIM (contínua)
```

---

## 💾 SISTEMA DE ARMAZENAMENTO

### Gravação Cíclica

```python
# Exemplo: Plano 7 dias
dias = [0, 1, 2, 3, 4, 5, 6]

# Quando atinge dia 7
if len(dias) >= 7:
    dias[0] = novo_dia  # Sobrescreve dia mais antigo
```

### Planos Disponíveis

| Plano | Dias | Usuários | Diferencial |
|-------|------|----------|-------------|
| Basic | 7    | 3        | -           |
| Pro   | 15   | 5        | -           |
| Premium | 30 | 10       | Relatórios  |

### Clipes Permanentes
- Usuário cria clipe de gravação
- Clipe NÃO é deletado no ciclo
- Armazenamento permanente

---

## 🔍 SENTINELA (Busca Retroativa)

### Funcionamento
1. Usuário define filtros (data, câmera, cor, tipo)
2. Sistema processa gravações (não tempo real)
3. YOLO detecta veículos
4. Retorna matches com timestamps
5. Usuário clica → pula para momento exato

### Casos de Uso
```
Cenário: Crime no dia 6
1. Abrir Sentinela
2. Filtrar: data=dia6, cor=preto, tipo=sedan
3. Sistema busca em gravações
4. Retorna veículos encontrados
5. Clicar → ver vídeo no momento
```

---

## 🎨 INTERFACE DO USUÁRIO

### Visualização de Câmeras

#### Lista (Padrão)
```
┌─────────────────────────────────────┐
│ 📹 Câmera 1 - Entrada    [▶️ Ver]  │
│ 📹 Câmera 2 - Saída      [▶️ Ver]  │
│ 📹 Câmera 3 - Garagem    [▶️ Ver]  │
└─────────────────────────────────────┘
```

#### Player Individual
```
Clique em "Ver" → Abre player único
```

#### Mosaicos
```
┌──────────┬──────────┐
│ Câmera 1 │ Câmera 2 │
├──────────┼──────────┤
│ Câmera 3 │ Câmera 4 │
└──────────┴──────────┘

Limite: 4 câmeras por mosaico
Mosaicos: Ilimitados
```

---

## 🔄 FLUXO DE DADOS

### 1. Streaming + Gravação
```
Câmera → MediaMTX → HLS (visualização)
                  ↓
              Gravação (MP4)
```

### 2. LPR Detection (RTSP apenas)
```
Câmera RTSP → LPR Service → YOLO → OCR → Placa detectada
                                              ↓
                                         Backend API
                                              ↓
                                         PostgreSQL
```

### 3. Sentinela (Busca)
```
Usuário → Filtros → Sentinela → Processa gravações → YOLO
                                                        ↓
                                                   Matches
                                                        ↓
                                                   Timeline
```

---

## 📊 PRÓXIMAS IMPLEMENTAÇÕES

### PHASE 1: Recording Service (3-4 dias)
**O que faz**: Gerencia gravação cíclica

**Tarefas**:
1. Storage Manager (lógica cíclica)
2. Models (Recording, Clip, Plan)
3. MediaMTX integration (enable recording)
4. Cleanup worker (deleta gravações antigas)

**Resultado**: Gravação cíclica 7/15/30 dias funciona

---

### PHASE 2: Playback & Timeline (2-3 dias)
**O que faz**: Navega em gravações

**Tarefas**:
1. Playback API (retorna segmentos)
2. Timeline component (barra de tempo)
3. Clip creator (criar clipes permanentes)

**Resultado**: Usuário navega em gravações, cria clipes

---

### PHASE 3: Sentinela (3-4 dias)
**O que faz**: Busca retroativa

**Tarefas**:
1. Detector (YOLO para veículos)
2. Search engine (processa gravações)
3. Search UI (formulário + resultados)
4. Background worker (processamento assíncrono)

**Resultado**: Busca retroativa funciona

---

### PHASE 4: Planos & Usuários (2 dias)
**O que faz**: Sistema de planos

**Tarefas**:
1. Plan models (7/15/30 dias)
2. User roles (superadmin, user)
3. Plan UI (gerenciamento)

**Resultado**: Planos funcionam, limites respeitados

---

### PHASE 5: UI Refactor (2 dias)
**O que faz**: Atualiza interface

**Tarefas**:
1. List view (padrão)
2. Mosaico limits (4 câmeras)
3. Navigation (rotas)

**Resultado**: UI refletindo nova arquitetura

---

## 🎯 DECISÕES TÉCNICAS

### Por que YOLO Legacy?
- ✅ Modelo já treinado
- ✅ Sem custo por frame
- ✅ Controle total
- ✅ Offline/On-premise

### Por que Gravação Cíclica?
- ✅ Sentinela precisa de histórico
- ✅ Investigação retroativa
- ✅ Sem perda de eventos
- ✅ Custo controlado (deleta antigos)

### Por que RTSP = LPR?
- ✅ Alta definição
- ✅ Melhor qualidade para OCR
- ✅ RTMP = bullets (baixa qualidade)

---

## 📈 MÉTRICAS DE SUCESSO

### MVP (7 dias)
- [ ] Gravação cíclica 7 dias
- [ ] LPR detecta placas RTSP
- [ ] Timeline navegável
- [ ] Clipes permanentes
- [ ] Lista de câmeras

### Completo (30 dias)
- [ ] Sentinela funcional
- [ ] 3 planos (7/15/30)
- [ ] Gerenciamento usuários
- [ ] Mosaicos 4 câmeras
- [ ] Relatórios (premium)

---

## 🚀 COMO INICIAR

```bash
# 1. Subir serviços
docker-compose up -d

# 2. Verificar status
docker-compose ps

# 3. Acessar
Frontend: http://localhost:5173
Backend: http://localhost:8000
Prometheus: http://localhost:9090
LPR Webhook: http://localhost:5000

# 4. Adicionar câmera RTSP (LPR ativa)
curl -X POST http://localhost:8000/api/cameras/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Camera LPR",
    "rtsp_url": "rtsp://...",
    "location": "Entrada"
  }'

# 5. Adicionar câmera RTMP (sem LPR)
curl -X POST http://localhost:8000/api/cameras/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Camera Bullet",
    "rtsp_url": "rtmp://...",
    "location": "Garagem"
  }'
```

---

## 📞 SUPORTE

- Logs: `docker-compose logs -f [service]`
- Health: `curl http://localhost:[port]/health`
- Restart: `docker-compose restart [service]`
