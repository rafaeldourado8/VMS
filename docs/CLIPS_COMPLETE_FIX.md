# Correção Completa - Sistema de Clips

## Problema

Os clips estavam sendo criados mas os vídeos não eram encontrados porque:
1. O `file_path` apontava para `/clips/` mas os vídeos reais estão em `/recordings/`
2. O serviço de clips processa os vídeos de forma assíncrona
3. O frontend não mostrava o status do processamento

## Solução Implementada

### 1. Backend - Views (apps/clips/views.py)

**Endpoint de vídeo atualizado:**
- Busca primeiro do serviço de clips (se `external_id` existe)
- Fallback para arquivo local se necessário
- Streaming do vídeo via proxy

**Novo endpoint de status:**
- `GET /api/clips/{id}/status/` - Verifica status do processamento
- Atualiza o banco quando clip está completo

### 2. Backend - URLs (apps/clips/urls.py)

Rotas simplificadas sem duplicação:
```
POST   /api/clips/              - Criar clip
GET    /api/clips/              - Listar clips
GET    /api/clips/{id}/         - Detalhes
GET    /api/clips/{id}/video/   - Download vídeo
GET    /api/clips/{id}/status/  - Status processamento
DELETE /api/clips/{id}/         - Remover
```

### 3. Frontend - API Service

Adicionado método `getStatus()` para verificar processamento:
```typescript
async getStatus(id: number): Promise<{ status: string }>
```

### 4. Frontend - UI (ClipsPage.tsx)

**Indicadores de status:**
- 🟡 Pending - Aguardando processamento
- 🔵 Processing - Processando vídeo
- 🟢 Completed - Pronto para assistir
- 🔴 Failed - Erro no processamento

**Botões desabilitados** quando clip não está pronto

### 5. Serviço de Clips (services/clips/main.py)

O serviço já estava correto:
- Busca vídeos em `/recordings/camera_{id}/{date}/`
- Corta e concatena segmentos MP4 de 60s
- Usa FFmpeg para criar o clip final
- Salva em `/clips/{clip_id}.mp4`

## Fluxo Completo

```
1. Usuário cria clip no frontend
   ↓
2. Backend cria registro com status='pending'
   ↓
3. Backend chama serviço de clips (assíncrono)
   ↓
4. Serviço busca segmentos em /recordings/
   ↓
5. FFmpeg processa e cria clip em /clips/
   ↓
6. Status muda para 'completed'
   ↓
7. Frontend pode assistir/baixar o vídeo
```

## Como Testar

1. **Reiniciar serviços:**
```bash
docker-compose restart backend clips
```

2. **Criar um clip:**
   - Acesse a página de Clips
   - Clique em "Criar Clip"
   - Selecione câmera, período e nome
   - Envie

3. **Verificar status:**
   - O clip aparecerá com badge de status
   - Aguarde o processamento (pode levar alguns segundos)
   - Quando ficar "Completed", pode assistir

4. **Assistir o vídeo:**
   - Clique em "Assistir"
   - O vídeo será carregado do serviço de clips

## Verificação de Logs

```bash
# Logs do serviço de clips
docker-compose logs -f clips

# Logs do backend
docker-compose logs -f backend
```

## Troubleshooting

### Clip fica em "pending" indefinidamente
- Verificar se serviço de clips está rodando
- Verificar logs: `docker-compose logs clips`
- Verificar se há gravações no período selecionado

### Erro 404 ao assistir vídeo
- Verificar se clip tem `external_id`
- Verificar se arquivo existe em `/clips/`
- Verificar logs do serviço de clips

### Vídeo não carrega
- Verificar se status é "completed"
- Verificar tamanho do arquivo (não pode ser 0 bytes)
- Testar download direto: `/api/clips/{id}/video/`
