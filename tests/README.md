# 🧪 TESTES VMS - Suite Completa de Testes

Esta pasta contém todos os testes para validar o desempenho, capacidade e funcionalidades do sistema VMS.

## 📋 Testes Disponíveis

### 1. 🎬 Teste de Streaming e Latência
**Arquivo:** `test_streaming_capacity.py`

**O que testa:**
- Streaming simultâneo de múltiplas câmeras
- Latência dos streams HLS
- Qualidade de reprodução
- Capacidade de viewers simultâneos

**Métricas:**
- Latência média/máxima/mínima
- Taxa de sucesso dos streams
- Qualidade geral (Excelente/Boa/Regular/Ruim)

### 2. 🤖 Teste de Detecções de IA
**Arquivo:** `test_detections.py`

**O que testa:**
- Status dos AI Workers
- Detecções ativas no sistema
- Configurações de ROI, linhas virtuais, zonas
- Atividade de detecção por câmera

**Métricas:**
- Workers ativos/inativos
- Total de detecções
- Detecções recentes (última hora)
- Nível de atividade

### 3. 🔥 Teste de Capacidade Máxima
**Arquivo:** `test_system_capacity.py`

**O que testa:**
- Capacidade máxima de câmeras simultâneas
- Uso de recursos (CPU, RAM)
- Performance dos containers Docker
- Limites do MediaMTX

**Métricas:**
- Máximo de câmeras suportadas
- Uso de CPU/RAM no pico
- Capacidade estimada recomendada

## 🚀 Como Executar

### Pré-requisitos
```bash
# Instalar dependências
pip install aiohttp psutil
```

### Execução Individual
```bash
# Teste de streaming
python tests/test_streaming_capacity.py

# Teste de detecções  
python tests/test_detections.py

# Teste de capacidade
python tests/test_system_capacity.py
```

### Execução Completa
```bash
# Executar todos os testes
tests/run_all_tests.bat
```

## 📹 Configuração de Câmeras de Teste

### Adicionar Câmeras Automaticamente
```bash
python tests/setup_test_cameras.py
```

### Lista de Câmeras Incluídas
- **9 câmeras RTSP** (45.236.226.x)
- **3 câmeras RTSP** (186.226.193.111, 170.84.217.84)  
- **3 streams RTMP** (Camerite services)

**Total: 15 câmeras de teste**

## 📊 Interpretação dos Resultados

### Streaming e Latência
- **🟢 Excelente:** < 1.0s latência
- **🟡 Boa:** 1.0-2.0s latência
- **🟠 Regular:** 2.0-3.0s latência
- **🔴 Ruim:** > 3.0s latência

### Detecções de IA
- **🟢 Alta:** > 10 detecções/hora
- **🟡 Média:** 5-10 detecções/hora
- **🟠 Baixa:** 1-5 detecções/hora
- **🔴 Nenhuma:** 0 detecções/hora

### Capacidade do Sistema
- **CPU < 70%:** Sistema pode suportar mais câmeras
- **CPU 70-85%:** Capacidade próxima do limite
- **CPU > 85%:** Sistema no limite máximo

## 🎯 Cenários de Teste

### Teste Básico (5 câmeras)
- Validar funcionamento básico
- Verificar latência inicial
- Confirmar detecções ativas

### Teste Médio (10-15 câmeras)
- Testar capacidade normal de uso
- Avaliar performance com carga média
- Verificar estabilidade

### Teste de Stress (25+ câmeras)
- Encontrar limite máximo
- Testar comportamento sob stress
- Identificar gargalos

## 🔧 Troubleshooting

### Erro de Login
```
❌ Falha no login
```
**Solução:** Criar usuário admin em http://localhost

### Câmeras não Conectam
```
❌ Câmera X: HTTP 400/500
```
**Solução:** Verificar URLs RTSP/RTMP e conectividade

### AI Workers Inativos
```
❌ AI Worker 1: Inativo
```
**Solução:** 
```bash
docker-compose restart ai_worker_1 ai_worker_2
```

### MediaMTX Indisponível
```
❌ MediaMTX API: Erro
```
**Solução:**
```bash
docker-compose restart mediamtx
```

## 📈 Benchmarks Esperados

### Sistema Básico (4GB RAM, 4 cores)
- **Câmeras simultâneas:** 10-15
- **Latência média:** 1-2s
- **CPU máximo:** 60-70%

### Sistema Médio (8GB RAM, 8 cores)  
- **Câmeras simultâneas:** 25-35
- **Latência média:** 0.5-1s
- **CPU máximo:** 50-60%

### Sistema Avançado (16GB RAM, 16 cores)
- **Câmeras simultâneas:** 50+
- **Latência média:** < 0.5s
- **CPU máximo:** 40-50%

## 🎯 Objetivos dos Testes

1. **Validar funcionalidades** implementadas
2. **Medir performance** real do sistema
3. **Identificar limites** de capacidade
4. **Otimizar configurações** para melhor desempenho
5. **Garantir qualidade** antes da produção

---

**💡 Dica:** Execute os testes em horários diferentes para avaliar variações de performance e conectividade das câmeras externas.