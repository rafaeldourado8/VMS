# Sprint 4: Retenção e Cleanup

## Objetivo
Implementar sistema de retenção automática e cleanup de arquivos antigos

## Checklist

### 🗑 Django - Cleanup Service
- [x] `cleanup_service.py`
  - [x] calculate_retention_dates()
  - [x] find_expired_files()
  - [x] delete_expired_files()
  - [x] log_cleanup_actions()
- [x] `retention_calculator.py`
  - [x] get_camera_retention_config()
  - [x] calculate_expiry_date()
  - [x] check_file_expired()

### ⏰ Celery Tasks
- [x] `cleanup_expired_recordings.py`
  - [x] Task periódica (diária)
  - [x] Processa uma câmera por vez
  - [x] Log detalhado de ações
  - [x] Retry em caso de erro
- [x] `audit_storage_usage.py`
  - [x] Calcula uso de storage
  - [x] Atualiza estatísticas
  - [x] Alerta de espaço baixo

### 📊 Django - Storage Stats
- [x] `storage_service.py`
  - [x] get_total_storage_usage()
  - [x] get_camera_storage_usage()
  - [x] get_retention_savings()
  - [x] calculate_projected_usage()
- [x] Endpoints de estatísticas
  - [x] `GET /api/timeline/storage/usage/` - Uso atual
  - [x] `GET /api/timeline/storage/projections/` - Projeções
  - [x] `GET /api/timeline/storage/cameras/` - Por câmera

### 🔄 FastAPI - Sync com Cleanup
- [x] Webhook para notificar FastAPI sobre cleanup
- [x] Invalidação automática de cache
- [x] Reindexação após cleanup
- [x] `POST /cleanup-notification` endpoint

### 📈 Algoritmos de Retenção
- [x] **FIFO (First In, First Out)**
  - [x] Remove arquivos mais antigos primeiro
  - [x] Respeita configuração de dias
- [x] **Smart Cleanup**
  - [x] Preserva arquivos com detecções
  - [x] Remove gaps primeiro
  - [x] Otimiza por espaço/importância
- [x] **Gradual Deletion**
  - [x] Não deleta tudo de uma vez
  - [x] Batch processing
  - [x] Throttling para não sobrecarregar I/O

### 🚨 Alertas e Monitoramento
- [x] `monitoring_service.py`
  - [x] check_disk_space()
  - [x] alert_low_space()
  - [x] monitor_cleanup_health()
- [x] Integração com sistema de alertas
- [x] Dashboard de storage no admin

### 🔒 Segurança e Validação
- [x] Validação antes de deletar
  - [x] Confirma que arquivo está expirado
  - [x] Verifica permissões
  - [x] Log de auditoria obrigatório
- [x] Backup de metadados antes de deletar
- [x] Rollback em caso de erro

### 📋 Configurações Avançadas
- [x] `RetentionPolicy` model
  - [x] preserve_detections (BooleanField)
  - [x] min_free_space_gb (IntegerField)
  - [x] cleanup_schedule (CharField)
  - [x] batch_size (IntegerField)
- [x] Configuração por tipo de arquivo
- [x] Exceções por câmera crítica

### 🗃 Auditoria Completa
- [x] Log de todas as operações
- [x] Rastreabilidade de deletions
- [x] Relatórios de economia de espaço
- [x] Histórico de configurações

### 📊 Dashboard Admin
- [x] Gráfico de uso de storage
- [x] Timeline de cleanup
- [x] Configuração de retenção por câmera
- [x] Logs de auditoria em tempo real

### ⚙️ Configurações Sistema
- [x] `RETENTION_CHECK_INTERVAL` - Intervalo de verificação
- [x] `CLEANUP_BATCH_SIZE` - Arquivos por batch
- [x] `MIN_FREE_SPACE_GB` - Espaço mínimo livre
- [x] `PRESERVE_DETECTIONS` - Preservar arquivos com detecções

### 🧪 Testes de Retenção
- [x] Teste de cálculo de expiração
- [x] Teste de cleanup automático
- [x] Teste de preservação de detecções
- [x] Teste de rollback em erro
- [x] Teste de performance com muitos arquivos

### 📈 Métricas
- [x] Espaço liberado por cleanup
- [x] Tempo médio de cleanup
- [x] Arquivos processados por minuto
- [x] Taxa de erro de cleanup

## Critérios de Aceite
- [x] Cleanup automático funciona diariamente
- [x] Arquivos expirados são removidos corretamente
- [x] Auditoria completa de todas as operações
- [x] Dashboard mostra estatísticas em tempo real
- [x] Performance não impacta gravações ativas
- [x] Sistema de alertas funciona

## Estimativa: 10 horas