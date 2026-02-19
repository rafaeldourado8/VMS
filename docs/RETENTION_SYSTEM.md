# Sistema de Retenção Automática de Gravações

## Visão Geral

O sistema implementa limpeza automática de gravações antigas baseado em política FIFO (First In, First Out) configurável por câmera.

## Como Funciona

### 1. Serviço de Limpeza (`retention_cleanup`)
- **Execução**: A cada 1 hora
- **Localização**: `services/recorder/retention_cleanup.py`
- **Container**: `gtvision_retention_cleanup`

### 2. Política de Retenção

Cada câmera pode ter uma política de retenção configurada:
- **7 dias**: Mantém últimos 7 dias, deleta anteriores
- **15 dias**: Mantém últimos 15 dias, deleta anteriores
- **30 dias**: Mantém últimos 30 dias, deleta anteriores (padrão)

### 3. Processo de Limpeza

```
1. Busca configuração de retenção de cada câmera no backend
2. Calcula data de corte: hoje - dias_retencao
3. Varre diretórios de gravação:
   - /recordings/camera_{id}/YYYY-MM-DD/
   - /recordings/cam_{id}/YYYY-MM-DD/
4. Deleta pastas com data < data_corte
5. Registra logs detalhados
```

## Exemplo Prático

**Câmera 1 com retenção de 7 dias:**
- Hoje: 2024-01-15
- Data de corte: 2024-01-08
- Ação: Deleta todas as pastas antes de 2024-01-08

```
/recordings/camera_1/
├── 2024-01-05/  ❌ DELETADO (3 dias antes do corte)
├── 2024-01-06/  ❌ DELETADO (2 dias antes do corte)
├── 2024-01-07/  ❌ DELETADO (1 dia antes do corte)
├── 2024-01-08/  ✅ MANTIDO (no limite)
├── 2024-01-09/  ✅ MANTIDO
├── ...
└── 2024-01-15/  ✅ MANTIDO (hoje)
```

## Configuração

### Alterar Retenção de uma Câmera

**Via API:**
```bash
curl -X PATCH http://localhost:8000/api/cameras/{id}/ \
  -H "Content-Type: application/json" \
  -d '{"recording_retention_days": 15}'
```

**Via Django Admin:**
1. Acesse http://localhost:8000/admin
2. Navegue até Cameras
3. Edite a câmera desejada
4. Altere o campo "Recording Retention Days"
5. Salve

### Alterar Intervalo de Verificação

Edite `services/recorder/retention_cleanup.py`:
```python
CHECK_INTERVAL = 3600  # 1 hora (em segundos)
```

Valores sugeridos:
- `1800` = 30 minutos
- `3600` = 1 hora (padrão)
- `7200` = 2 horas
- `86400` = 1 dia

## Monitoramento

### Verificar Status
```bash
# Windows
scripts\check_retention.bat

# Linux/Mac
curl http://localhost:8003/recordings/retention-status | jq
```

### Logs do Serviço
```bash
docker logs gtvision_retention_cleanup -f
```

### Exemplo de Log
```
============================================================
LIMPEZA AUTOMATICA DE RETENCAO (FIFO)
============================================================
Camera 1: Retencao 7 dias | Deletar antes de 2024-01-08
  [DELETANDO] 2024-01-05: 1440 arquivos, 2.5 GB
  [DELETANDO] 2024-01-06: 1440 arquivos, 2.5 GB
  [DELETANDO] 2024-01-07: 1440 arquivos, 2.5 GB
Camera 2: Retencao 15 dias | Deletar antes de 2023-12-31
  [OK] Nenhuma gravacao antiga para deletar
============================================================
RESUMO: 2 cameras processadas
TOTAL: 4320 arquivos deletados | 7.5 GB liberados
Espaco liberado: 7.50 GB
============================================================
```

## Segurança

### Proteções Implementadas
1. ✅ Apenas deleta arquivos `.mp4`
2. ✅ Valida formato de data (YYYY-MM-DD)
3. ✅ Tratamento de erros por pasta
4. ✅ Logs detalhados de cada operação
5. ✅ Não deleta gravações dentro do período de retenção

### Recuperação de Desastre
- Gravações são deletadas permanentemente
- Não há lixeira ou backup automático
- Recomendação: Configure backup externo para gravações críticas

## Troubleshooting

### Serviço não está rodando
```bash
docker-compose up -d retention_cleanup
docker logs gtvision_retention_cleanup
```

### Gravações não estão sendo deletadas
1. Verifique logs: `docker logs gtvision_retention_cleanup`
2. Confirme política de retenção: `scripts\check_retention.bat`
3. Verifique permissões do volume `/recordings`

### Espaço em disco cheio
Execute limpeza manual:
```bash
docker exec gtvision_retention_cleanup python retention_cleanup.py
```

## Estatísticas

### Espaço Economizado
- **1 câmera 1080p**: ~3.5 GB/dia
- **Retenção 7 dias**: Economiza ~105 GB após 30 dias
- **Retenção 15 dias**: Economiza ~52.5 GB após 30 dias

### Cálculo de Espaço Necessário
```
Espaço = Câmeras × Bitrate × Horas/dia × Dias_retenção

Exemplo:
- 10 câmeras
- 4 Mbps cada
- 24h/dia
- 7 dias retenção
= 10 × 4 × 24 × 7 / 8 = 840 GB
```

## Melhores Práticas

1. **Câmeras críticas**: 30 dias de retenção
2. **Câmeras normais**: 15 dias de retenção
3. **Câmeras de baixa prioridade**: 7 dias de retenção
4. **Monitoramento**: Verificar logs semanalmente
5. **Backup**: Exportar gravações importantes antes da expiração
