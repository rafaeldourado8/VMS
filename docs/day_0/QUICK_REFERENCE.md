# Day 0 - Quick Reference

## Serviços Implementados

### 1. Recorder Service
**Porta**: N/A (interno)  
**Função**: Re-encode streams para 2Mbps  
**Storage**: `/recordings/cam_{id}/YYYY-MM-DD/HH-MM-SS.mp4`

### 2. Clips Service
**Porta**: 8004  
**Função**: Extração de segmentos de vídeo  
**Endpoints**:
- `POST /clips/create`
- `GET /clips/{id}`
- `GET /clips/{id}/download`
- `DELETE /clips/{id}`

### 3. Streaming Service (atualizado)
**Porta**: 8001  
**Novo endpoint**: `GET /cameras/{id}/snapshot`

---

## Configurações Importantes

### MediaMTX (mediamtx.yml)
```yaml
sourceOnDemand: no    # Stream sempre ativo
record: no            # Gravação via Recorder Service
recordDeleteAfter: 168h
```

### Docker Compose
```yaml
# Novos serviços
recorder:
  volumes:
    - recordings:/recordings

clips:
  ports:
    - "8004:8000"
  volumes:
    - clips_storage:/clips
```

---

## Storage Estimado

| Câmeras | Dias | Storage (2Mbps) |
|---------|------|-----------------|
| 1       | 7    | 139 GB          |
| 6       | 7    | 834 GB          |
| 12      | 7    | 1.7 TB          |
| 24      | 7    | 3.3 TB          |

---

## Comandos Rápidos

```bash
# Rebuild serviços
docker-compose up -d --build recorder clips

# Logs
docker-compose logs -f recorder
docker-compose logs -f clips

# Espaço usado
docker exec vms-recorder-1 du -sh /recordings

# Limpar gravações antigas (>7 dias)
docker exec vms-recorder-1 find /recordings -mtime +7 -delete
```

---

## Estrutura de Arquivos Criados/Modificados

```
VMS/
├── docker-compose.yml              [MODIFICADO]
├── mediamtx.yml                    [MODIFICADO]
├── services/
│   ├── recorder/                   [NOVO]
│   │   ├── recorder.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── clips/                      [NOVO]
│   │   ├── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── streaming/
│       └── main.py                 [MODIFICADO - snapshot endpoint]
├── backend/apps/clips/             [NOVO]
│   ├── models.py
│   ├── views.py
│   └── serializers.py
├── frontend/src/
│   ├── components/cameras/
│   │   └── StreamThumbnail.tsx    [MODIFICADO]
│   └── pages/
│       └── CamerasPage.tsx        [MODIFICADO]
└── docs/
    ├── day_0/                      [NOVO]
    │   ├── README.md
    │   └── QUICK_REFERENCE.md
    ├── alpr/
    ├── analytics/
    └── clips/
```

---

## Issues Resolvidos Hoje

1. ✅ RabbitMQ Erlang Cookie error
2. ✅ Snapshot polling consumindo banda
3. ✅ Storage excessivo (4.15TB → 1.7TB)
4. ✅ Grid view desnecessário
5. ✅ Recorder 401 error handling

---

## Próximos Passos

1. [ ] Resolver autenticação Recorder ↔ Backend
2. [ ] Implementar ALPR offline
3. [ ] Dashboard de storage
4. [ ] Testes de carga (12+ câmeras)
