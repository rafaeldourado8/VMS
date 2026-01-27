# Commit Atômico - Fase 1

## Mensagem do commit

```
feat: infraestrutura base com NGINX, MediaMTX e HLS player

Implementa Fase 1 do MVP VMS Municipal:
- Docker Compose com NGINX + MediaMTX
- NGINX como reverse proxy (frontend + HLS streams)
- MediaMTX configurado para low-latency HLS
- Frontend minimalista com HLS.js player
- Câmeras adicionadas dinamicamente via API MediaMTX
- Teste automatizado com 3 streams reais (RTSP/RTMP/IP)

Checklist:
✅ docker-compose sobe sem erro
✅ NGINX responde em :80
✅ MediaMTX entrega streams HLS
✅ Frontend abre vídeo no browser
✅ API MediaMTX funcional para adicionar câmeras

Refs: RULES.md Fase 1 (Dia 1-2)
```

## Arquivos modificados/criados

```
vms/
├── docker-compose.yml                                    # NOVO
├── docs/
│   └── fase1-infra/
│       └── README.md                                     # NOVO
├── src/
│   ├── frontend/
│   │   └── index.html                                    # NOVO
│   └── infrastructure/
│       ├── nginx/
│       │   └── nginx.conf                                # NOVO
│       ├── servers/
│       │   └── mediamtx.yml                              # MODIFICADO
│       └── test/
│           └── streams/
│               ├── README.md                             # NOVO
│               ├── test.html                             # NOVO
│               ├── add_cameras.bat                       # NOVO
│               ├── add_cameras.sh                        # NOVO
│               └── test_cameras.bat                      # NOVO (não usado)
```

## Comando para commit

```bash
git add vms/docker-compose.yml
git add vms/docs/fase1-infra/
git add vms/src/frontend/index.html
git add vms/src/infrastructure/nginx/nginx.conf
git add vms/src/infrastructure/servers/mediamtx.yml
git add vms/src/infrastructure/test/streams/

git commit -m "feat: infraestrutura base com NGINX, MediaMTX e HLS player

Implementa Fase 1 do MVP VMS Municipal:
- Docker Compose com NGINX + MediaMTX
- NGINX como reverse proxy (frontend + HLS streams)
- MediaMTX configurado para low-latency HLS
- Frontend minimalista com HLS.js player
- Câmeras adicionadas dinamicamente via API MediaMTX
- Teste automatizado com 3 streams reais (RTSP/RTMP/IP)

Checklist:
✅ docker-compose sobe sem erro
✅ NGINX responde em :80
✅ MediaMTX entrega streams HLS
✅ Frontend abre vídeo no browser
✅ API MediaMTX funcional para adicionar câmeras

Refs: RULES.md Fase 1 (Dia 1-2)"
```

## Validação antes do commit

```bash
# 1. Ambiente sobe sem erro
docker-compose up -d

# 2. NGINX responde
curl -I http://localhost

# 3. MediaMTX API responde
curl http://localhost:9997/v3/paths/list

# 4. Câmeras estão ativas
docker logs vms_ffmpeg_test

# 5. Frontend carrega
# Abrir http://localhost no browser

# 6. Stream funciona
# Digitar "camera_rtsp" e clicar em Carregar
```

## Notas

- Commit atômico: toda a Fase 1 em um único commit
- Funcionalidade completa e testada
- Documentação incluída
- Pronto para Fase 2 (Django + FastAPI)
