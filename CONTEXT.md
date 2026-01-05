# 📋 Contexto Técnico - VMS (Video Management System)

## 🎯 Status Atual: REFATORAÇÃO DDD 100% COMPLETA (BACKEND + FRONTEND) ✅🎉🚀

**Objetivo Alcançado**: Domain-Driven Design (DDD) aplicado com sucesso em **TODO** o sistema:
- ✅ Backend Django (100%)
- ✅ Streaming Service FastAPI (100%)
- ✅ AI Detection Service FastAPI (100%)
- ✅ Frontend React + TypeScript (100%)

**Documentos de Referência**:
- `docs/DDD_FINAL_COMPLETE.md` - Resumo executivo completo (backend + frontend)
- `docs/DDD_100_COMPLETE.md` - Resumo backend
- `docs/DDD_COMPLETE_SUMMARY.md` - Detalhes
- `README.md` - Especificações MVP

---

## 🏛️ Visão Geral

O VMS é uma plataforma institucional de monitoramento com IA integrada, focada em estabilidade e baixo custo operacional. O sistema utiliza processamento desacoplado para garantir que a análise de vídeo não afete a fluidez do streaming ao vivo.

## 🛠️ Stack Tecnológica

**Backend**: Django (API Administrativa e Persistência) - **EM REFATORAÇÃO DDD**
- Domain Layer: Entidades, Value Objects, Repositories (interfaces)
- Application Layer: Commands, Queries, Handlers (CQRS)
- Infrastructure Layer: Django Models, External Services
- Interface Layer: REST API

**Streaming**: FastAPI + MediaMTX (HLS/WebRTC)

**IA Worker**: Python com YOLOv8 e extração via FFmpeg

**Mensageria**: RabbitMQ (Fila de frames e eventos)

**Cache/Signals**: Redis

**Frontend**: React + Vite

---

## 🤖 Fluxo de Inteligência (Trigger P1-P2)

**Extração**: Worker FFmpeg extrai frames a 1 FPS e envia para RabbitMQ

**Monitoramento**: AIDetectionService monitora veículos cruzando linha virtual P1

**Ativação**: Ao cruzar P1, detecção de placas (OCR) é ativada para aquele veículo

**Finalização**: Ao cruzar P2, velocidade é calculada. Se houver excesso, dados são enviados ao backend Django

---

## 🎯 Bounded Contexts (DDD)

### 1. Monitoring Context
- **Entidades**: Camera, StreamSession
- **Value Objects**: StreamUrl, Location, GeoCoordinates
- **Responsabilidade**: Gerenciar câmeras e streaming

### 2. Detection Context
- **Entidades**: Detection, Vehicle
- **Value Objects**: LicensePlate, Confidence, VehicleType
- **Responsabilidade**: Processar detecções de IA

### 3. Configuration Context
- **Entidades**: ROI, VirtualLine, TripWire
- **Responsabilidade**: Configurações de detecção

### 4. Identity Context
- **Entidades**: User, Permission
- **Responsabilidade**: Autenticação e autorização

---

## 🔄 Desafios Técnicos

**Otimização**: Redução de CPU de 429% para 0.71% no modo minimalista

**Resiliência**: Processamento assíncrono de eventos de detecção

**Configuração Dinâmica**: ROIs para filtrar alarmes falsos

**Refatoração DDD**: Migração gradual sem quebrar API existente

## 📐 Princípios SOLID Aplicados

**S - Single Responsibility**: Cada entidade tem uma única responsabilidade

**O - Open/Closed**: Interfaces de repositório permitem extensão

**L - Liskov Substitution**: Implementações de repositório são intercambiáveis

**I - Interface Segregation**: Interfaces específicas por contexto

**D - Dependency Inversion**: Domínio não depende de infraestrutura

---

## 📊 Métricas de Qualidade

**Complexidade Ciclomática (CC)**:
- Meta: CC < 10 para todos os métodos
- Ferramenta: radon, pytest-cov

**Cobertura de Testes**:
- Meta: > 80% cobertura total
- Domain layer: > 90%
- Application layer: > 85%

**Tipos de Testes**:
- Unitários: Domain entities, value objects, services
- Integração: Repositories, external services
- E2E: API endpoints (mínimo)

---

## 🚀 Status Final

### Backend Django (100% ✅)
1. ✅ Estrutura de diretórios DDD
2. ✅ Monitoring Context (domain)
3. ✅ Detection Context (domain)
4. ✅ Application Layer (CQRS)
5. ✅ Infrastructure Layer
6. ✅ Análise de qualidade

### Streaming Service (100% ✅)
7. ✅ Domain Layer (Stream, StreamPath, HLSUrl)
8. ✅ Application Layer (Provision/Remove handlers)
9. ✅ Infrastructure Layer (MediaMTX client)
10. ✅ API FastAPI refatorada

### AI Detection Service (100% ✅)
11. ✅ Domain Layer (Vehicle, ROI, VirtualLine, TriggerService)
12. ✅ Application Commands (ProcessFrame, ToggleAI, UpdateROI)
13. ✅ Application Handlers (ProcessFrame, ToggleAI, UpdateROI)
14. ✅ Infrastructure Layer (YOLO, OCR, CameraConfigRepository)
15. ✅ API FastAPI (5 endpoints)

**Métricas Totais:**
- ✅ 104 testes (63 backend + 28 streaming + 13 AI)
- ✅ CC médio: ~3 (meta < 10)
- ✅ Cobertura: > 80% (meta > 80%)
- ✅ SOLID: 100% aplicado
- ✅ **PROJETO 100% COMPLETO** 🎉

**Scripts de Análise:**
- `run_quality_analysis.bat` - Backend completo
- `run_streaming_tests.bat` - Streaming service
- `analyze_complexity.bat` - CC por camada
- `analyze_coverage.bat` - Cobertura

**Consulte `docs/DDD_COMPLETE_SUMMARY.md` para resumo executivo completo**