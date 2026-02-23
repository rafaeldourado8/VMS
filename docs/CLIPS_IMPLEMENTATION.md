# Implementação de Clips - Sistema VMS

## Resumo das Mudanças

### 1. Backend - Proteção de Clips

**Arquivo**: `backend/apps/clips/views.py`

- Adicionado endpoint `/api/clips/protected-files/` (público)
- Retorna lista de arquivos protegidos para o retention service
- Permite que o serviço de retenção consulte quais arquivos não devem ser deletados

```python
@action(detail=False, methods=['get'], permission_classes=[AllowAny])
def protected_files(self, request):
    """Retorna lista de arquivos protegidos (clips) para o retention service"""
    protected_clips = Clip.objects.filter(is_protected=True).values_list('file_path', flat=True)
    return Response({'protected_files': list(protected_clips)})
```

### 2. Retention Service - Verificação de Clips

**Arquivo**: `services/recorder/retention_cleanup.py`

- Integrado verificação de clips protegidos antes de deletar gravações
- Busca lista de arquivos protegidos via API do backend
- Pula pastas que contêm clips protegidos
- Log detalhado de clips mantidos

**Fluxo**:
1. Busca políticas de retenção das câmeras
2. Busca lista de clips protegidos (`/api/clips/protected-files/`)
3. Para cada pasta de gravação antiga:
   - Verifica se contém clips protegidos
   - Se SIM: mantém pasta inteira
   - Se NÃO: deleta conforme política FIFO

### 3. Frontend - ClipesPage Melhorada

**Arquivo**: `frontend/src/pages/ClipsPage.tsx`

#### Funcionalidades Adicionadas:

1. **Modal de Criação de Clips**
   - Botão "Criar Clip" no topo da página
   - Formulário com:
     - Seleção de câmera
     - Nome do clip
     - Data/hora de início
     - Data/hora de fim
   - Validação de campos obrigatórios

2. **Player de Clips Aprimorado**
   - Modal fullscreen com player HTML5
   - Exibe informações completas:
     - Nome do clip
     - Câmera
     - Período (início - fim)
   - Controles nativos do navegador
   - Autoplay ao abrir

3. **UI/UX Melhorada**
   - Estado vazio com call-to-action
   - Grid responsivo (1/2/3 colunas)
   - Cards com hover effects
   - Thumbnails ou ícone de play
   - Duração visível no card
   - Ações rápidas: Assistir, Download, Deletar

4. **Busca e Filtros**
   - Busca por nome do clip ou câmera
   - Filtro em tempo real

### 4. Componente Label

**Arquivo**: `frontend/src/components/ui/index.tsx`

- Adicionado componente Label para formulários
- Estilo consistente com design system

## Modelo de Dados

### Clip (Backend)

```python
class Clip(models.Model):
    owner = ForeignKey(User)
    camera = ForeignKey(Camera, null=True)
    camera_id_backup = IntegerField()
    camera_name_backup = CharField()
    name = CharField()
    start_time = DateTimeField()
    end_time = DateTimeField()
    file_path = CharField()
    thumbnail_path = CharField(null=True)
    duration_seconds = IntegerField()
    file_size_bytes = BigIntegerField()
    is_protected = BooleanField(default=True)  # ⭐ PROTEÇÃO
    status = CharField(default='pending')
    created_at = DateTimeField()
```

### Clip (Frontend)

```typescript
interface Clip {
  id: number
  name: string
  camera: Camera
  start_time: string
  end_time: string
  file_path: string
  video_url?: string
  thumbnail_path: string | null
  duration_seconds: number
  created_at: string
}
```

## Fluxo de Criação de Clip

```
1. Usuário clica "Criar Clip"
   ↓
2. Preenche formulário:
   - Câmera
   - Nome
   - Início/Fim
   ↓
3. Frontend → POST /api/clips/
   ↓
4. Backend:
   - Valida dados
   - Cria registro no banco
   - is_protected = True (padrão)
   - Envia job para Clips Service
   ↓
5. Clips Service:
   - Localiza gravação
   - Recorta segmento com FFmpeg
   - Salva em /clips/
   - Atualiza status
   ↓
6. Frontend atualiza lista
```

## Fluxo de Proteção na Retenção

```
1. Retention Service (a cada 1h)
   ↓
2. Busca políticas de retenção
   ↓
3. Busca clips protegidos
   GET /api/clips/protected-files/
   ↓
4. Para cada pasta antiga:
   ├─ Tem clips protegidos?
   │  ├─ SIM → MANTÉM pasta
   │  └─ NÃO → DELETA pasta
   ↓
5. Log de resumo:
   - Arquivos deletados
   - Clips protegidos mantidos
   - Espaço liberado
```

## Endpoints da API

### Clips

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/clips/` | Lista clips do usuário |
| POST | `/api/clips/` | Cria novo clip |
| GET | `/api/clips/{id}/` | Detalhes do clip |
| DELETE | `/api/clips/{id}/` | Remove clip |
| GET | `/api/clips/{id}/video/` | Stream do vídeo |
| GET | `/api/clips/protected-files/` | Lista arquivos protegidos |

## Configurações

### Retenção Automática

- **Intervalo**: 1 hora
- **Política**: FIFO (First In, First Out)
- **Proteção**: Clips com `is_protected=True` nunca são deletados
- **Padrão**: 7 dias (se câmera não configurada)

### Clips Service

- **Duração máxima**: 5 minutos
- **Qualidades**: low (CRF 28), medium (CRF 18), high (CRF 15)
- **Formato**: MP4 (H.264 + AAC)
- **Diretório**: `/clips/`

## Testes

### Testar Criação de Clip

```bash
curl -X POST http://localhost/api/clips/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": 1,
    "name": "Teste Clip",
    "start_time": "2024-01-20T10:00:00",
    "end_time": "2024-01-20T10:05:00"
  }'
```

### Testar Proteção

```bash
# Listar clips protegidos
curl http://localhost/api/clips/protected-files/

# Verificar logs do retention service
docker logs vms-recorder-1 -f
```

## Próximos Passos

1. ✅ Proteção de clips na retenção
2. ✅ UI/UX melhorada
3. ✅ Modal de criação
4. ✅ Player aprimorado
5. 🔄 Geração de thumbnails automática
6. 🔄 Compartilhamento de clips
7. 🔄 Exportação em diferentes qualidades
8. 🔄 Integração com timeline (criar clip direto da timeline)

## Observações

- Clips são SEMPRE protegidos por padrão (`is_protected=True`)
- Usuário pode deletar manualmente via UI
- Retenção automática NUNCA deleta clips
- Clips mantêm referência histórica da câmera mesmo se câmera for deletada
