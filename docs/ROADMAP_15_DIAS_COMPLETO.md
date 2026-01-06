# 🚀 Roadmap Completo 15 Dias - VMS Production Ready

**Do estado atual → Sistema completo em produção**

---

## 📅 Visão Geral

| Semana | Foco | Entregas | Dias |
|--------|------|----------|------|
| **1** | IA Rekognition Otimizada | Detecção de placas econômica | 1-5 |
| **2** | Segurança OWASP + UI/UX | Sistema seguro e profissional | 6-10 |
| **3** | Playback + Recorte | Funcionalidades avançadas | 11-15 |

---

## 🎯 SEMANA 1: IA Rekognition (Custo Mínimo)

### **Objetivo:** Detecção de placas gastando < $50/mês

### **DIA 1: Setup AWS + Filtros Locais (6h)**
```
✅ Criar conta AWS + IAM user
✅ Configurar billing alerts ($25, $50, $100)
✅ Implementar Motion Detection (OpenCV)
✅ Implementar ROI Filter
✅ Implementar Cooldown Manager (60s)
```

**Código:**
- `backend/apps/deteccoes/motion_detector.py`
- `backend/apps/deteccoes/roi_filter.py`
- `backend/apps/deteccoes/cooldown_manager.py`

**Resultado:** Filtros locais reduzem 99% das chamadas (grátis)

---

### **DIA 2: Integração Rekognition (6h)**
```
✅ Instalar boto3
✅ Criar RekognitionService
✅ Criar AI Worker Otimizado (cascata de filtros)
✅ Testar detecção manual
```

**Código:**
- `backend/apps/deteccoes/rekognition_service.py`
- `backend/apps/deteccoes/ai_worker_optimized.py`
- `backend/apps/deteccoes/management/commands/run_ai_worker.py`

**Resultado:** Rekognition funcionando com filtros

---

### **DIA 3: Métricas + Testes (6h)**
```
✅ Implementar sistema de métricas
✅ Endpoint GET /api/ai/stats/
✅ Testar com 4 câmeras por 1 hora
✅ Validar custo real AWS
✅ Ajustar cooldown se necessário
```

**Código:**
- `backend/apps/deteccoes/metrics.py`
- `backend/apps/deteccoes/views.py` (stats endpoint)

**Resultado:** Custo validado < $50/mês

---

### **DIA 4: Frontend IA (6h)**
```
✅ Endpoint POST /cameras/{id}/toggle_ai/
✅ Componente CameraAIToggle
✅ Dashboard de métricas (frames, custos, detecções)
✅ Página de detecções com filtros
```

**Código:**
- `frontend/src/components/CameraAIToggle.tsx`
- `frontend/src/components/AIMetricsDashboard.tsx`
- `frontend/src/pages/DetectionsPage.tsx`

**Resultado:** Interface completa de IA

---

### **DIA 5: Deploy + Buffer (6h)**
```
✅ Configurar docker-compose com ai_worker
✅ Deploy em servidor de testes
✅ Validar logs e métricas
✅ Documentar setup
✅ Correções de bugs
```

**Documentação:**
- `docs/AI_REKOGNITION_SETUP.md`
- `docs/AI_COST_OPTIMIZATION.md`

**✅ ENTREGA SEMANA 1:** IA funcionando com custo otimizado

---

## 🔒 SEMANA 2: Segurança OWASP + UI/UX

### **Objetivo:** Sistema seguro e interface profissional

### **DIA 6: Auditoria de Segurança (6h)**
```
✅ Scan de vulnerabilidades (safety, npm audit)
✅ Atualizar dependências críticas
✅ Análise OWASP Top 10:
   - A01: Broken Access Control
   - A02: Cryptographic Failures
   - A03: Injection
   - A05: Security Misconfiguration
   - A07: Authentication Failures
```

**Ferramentas:**
```bash
# Backend
safety check
bandit -r backend/

# Frontend
npm audit
npm audit fix
```

**Resultado:** Zero vulnerabilidades críticas

---

### **DIA 7: Rate Limiting + Headers (6h)**
```
✅ Implementar rate limiting:
   - Login: 5 tentativas/minuto
   - API: 100 req/minuto
   - Ingest: 10 req/segundo
✅ Configurar security headers:
   - HSTS
   - X-Frame-Options
   - Content-Security-Policy
   - X-Content-Type-Options
✅ Forçar HTTPS em produção
```

**Código:**
```python
# backend/config/settings.py
SECURE_HSTS_SECONDS = 31536000
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True

# Rate limiting
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

**Resultado:** Sistema protegido contra ataques comuns

---

### **DIA 8: Autenticação Avançada (6h)**
```
✅ Refresh token automático
✅ Logout automático após 3min inatividade
✅ Auditoria de acessos (AccessLog model)
✅ Middleware de logging
✅ Endpoint de consulta de logs (admin only)
```

**Código:**
```python
# backend/apps/usuarios/models.py
class AccessLog(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
        ]
```

**Frontend:**
```typescript
// Detector de inatividade
useEffect(() => {
  let timeout;
  
  const resetTimer = () => {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      // Logout após 3 minutos
      logout();
    }, 3 * 60 * 1000);
  };
  
  window.addEventListener('mousemove', resetTimer);
  window.addEventListener('keypress', resetTimer);
  
  return () => {
    clearTimeout(timeout);
    window.removeEventListener('mousemove', resetTimer);
    window.removeEventListener('keypress', resetTimer);
  };
}, []);
```

**Resultado:** Autenticação robusta e auditável

---

### **DIA 9: UI/UX Profissional (6h)**
```
✅ Design system (cores, tipografia, espaçamentos)
✅ Componentes padronizados
✅ Dashboard analítico:
   - Cards de métricas
   - Gráfico de detecções (7 dias)
   - Status de câmeras
   - Custo AWS estimado
✅ Loading states
✅ Empty states
✅ Toasts de feedback
```

**Componentes:**
- `frontend/src/components/ui/` (shadcn/ui)
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/components/MetricsCard.tsx`
- `frontend/src/components/DetectionsChart.tsx`

**Resultado:** Interface profissional e intuitiva

---

### **DIA 10: Acessibilidade + Testes (6h)**
```
✅ WCAG 2.1 Level AA:
   - aria-labels
   - Navegação por teclado
   - Contraste de cores (4.5:1)
   - Screen reader friendly
✅ Responsividade:
   - Mobile (320px+)
   - Tablet (768px+)
   - Desktop (1024px+)
✅ Testes de segurança:
   - Penetration testing básico
   - CSRF validation
   - XSS prevention
✅ Testes de carga (Locust):
   - 50 usuários simultâneos
   - 100 req/s
```

**Ferramentas:**
```bash
# Acessibilidade
npm install --save-dev axe-core
npm run test:a11y

# Carga
locust -f backend/locustfile.py --host=http://localhost:8000
```

**✅ ENTREGA SEMANA 2:** Sistema seguro e profissional

---

## 🎥 SEMANA 3: Playback + Recorte

### **Objetivo:** Funcionalidades avançadas de vídeo

### **DIA 11: Sistema de Gravação (6h)**
```
✅ Configurar MediaMTX recording:
   - Formato: MP4
   - Segmentos: 1 hora
   - Retenção: 7 dias
✅ Model Recording (camera, start, end, path, size)
✅ Management command: scan_recordings
✅ Cronjob a cada 5 minutos
✅ API: GET /api/recordings/?camera_id=1&date=2025-01-15
```

**Configuração:**
```yaml
# mediamtx.yml
paths:
  all:
    record: yes
    recordPath: /recordings/%path/%Y-%m-%d_%H-%M-%S
    recordFormat: mp4
    recordSegmentDuration: 3600s
    recordDeleteAfter: 168h  # 7 dias
```

**Código:**
```python
# backend/apps/clips/models.py
class Recording(models.Model):
    camera = models.ForeignKey(Camera, on_delete=CASCADE)
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField()
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField()  # bytes
    duration = models.IntegerField()  # segundos
    status = models.CharField(max_length=20, default='available')
    
    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['camera', '-start_time']),
        ]
```

**Resultado:** Gravações automáticas funcionando

---

### **DIA 12: Player de Playback (6h)**
```
✅ Componente VideoPlayer (video.js ou plyr)
✅ Controles: play, pause, seek, volume, speed, fullscreen
✅ Página PlaybackPage:
   - Seletor de câmera
   - Seletor de data/hora
   - Player integrado
✅ Timeline de 24h com segmentos
✅ Marcadores de detecções
```

**Código:**
```typescript
// frontend/src/components/VideoPlayer.tsx
import Plyr from 'plyr-react';
import 'plyr-react/plyr.css';

export function VideoPlayer({ src, onTimeUpdate }) {
  return (
    <Plyr
      source={{
        type: 'video',
        sources: [{ src, type: 'video/mp4' }],
      }}
      options={{
        controls: ['play', 'progress', 'current-time', 'mute', 'volume', 'fullscreen'],
        speed: { selected: 1, options: [0.5, 1, 1.5, 2] },
      }}
      onTimeUpdate={onTimeUpdate}
    />
  );
}
```

```typescript
// frontend/src/components/RecordingTimeline.tsx
export function RecordingTimeline({ recordings, detections, onSeek }) {
  return (
    <div className="timeline">
      {/* Barra de 24h */}
      <div className="timeline-bar">
        {recordings.map(rec => (
          <div
            key={rec.id}
            className="segment"
            style={{
              left: `${getPosition(rec.start_time)}%`,
              width: `${getDuration(rec)}%`,
            }}
            onClick={() => onSeek(rec.start_time)}
          />
        ))}
      </div>
      
      {/* Marcadores de detecções */}
      {detections.map(det => (
        <div
          key={det.id}
          className="marker"
          style={{ left: `${getPosition(det.timestamp)}%` }}
          title={`Placa: ${det.plate}`}
        />
      ))}
    </div>
  );
}
```

**Resultado:** Playback funcional com timeline

---

### **DIA 13: Recorte e Exportação (6h)**
```
✅ Componente ClipSelector (drag para selecionar)
✅ API: POST /api/clips/create/
✅ Celery task para processar recorte (ffmpeg)
✅ Status: pending, processing, completed, failed
✅ Endpoint: GET /api/clips/{id}/download/
✅ Link temporário (1 hora de validade)
✅ Log de downloads (auditoria)
```

**Código:**
```python
# backend/apps/clips/tasks.py
from celery import shared_task
import subprocess

@shared_task
def create_clip(recording_id, start_time, end_time):
    recording = Recording.objects.get(id=recording_id)
    
    output_path = f"/media/clips/clip_{recording_id}_{start_time}.mp4"
    
    # FFmpeg para recortar
    cmd = [
        'ffmpeg',
        '-i', recording.file_path,
        '-ss', start_time,
        '-to', end_time,
        '-c', 'copy',  # Sem recodificação (rápido)
        output_path
    ]
    
    subprocess.run(cmd, check=True)
    
    # Criar registro
    clip = Clip.objects.create(
        recording=recording,
        start_time=start_time,
        end_time=end_time,
        file_path=output_path,
        status='completed'
    )
    
    return clip.id
```

```python
# backend/apps/clips/views.py
class ClipViewSet(viewsets.ModelViewSet):
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        clip = self.get_object()
        
        # Gerar link temporário
        token = generate_temp_token(clip.id, expires_in=3600)
        url = f"/media/clips/download/{token}/"
        
        # Log de auditoria
        DownloadLog.objects.create(
            user=request.user,
            clip=clip,
            ip_address=get_client_ip(request)
        )
        
        return Response({'download_url': url})
```

**Resultado:** Recorte e exportação funcionando

---

### **DIA 14: Testes Finais (6h)**
```
✅ Testes end-to-end:
   - Login → Câmeras → Ativar IA → Detecções
   - Playback → Selecionar intervalo → Recortar → Download
   - Logout automático (3min)
✅ Testes de performance:
   - 10 usuários simultâneos
   - 4 câmeras ao vivo
   - 2 playbacks simultâneos
✅ Testes de segurança:
   - Penetration testing
   - Rate limiting
   - CSRF/XSS
✅ Correções críticas
```

**Checklist:**
- [ ] Streaming estável (latência < 3s)
- [ ] IA detectando placas (acurácia > 85%)
- [ ] Custo AWS < $50/mês
- [ ] Playback sem travamentos
- [ ] Recorte funcionando (< 30s)
- [ ] Download seguro
- [ ] Zero vulnerabilidades críticas
- [ ] Interface responsiva

**Resultado:** Sistema validado e pronto

---

### **DIA 15: Entrega e Documentação (6h)**
```
✅ Documentação completa:
   - README.md atualizado
   - DEPLOYMENT_GUIDE.md
   - ADMIN_GUIDE.md
   - USER_MANUAL.md
   - API_DOCUMENTATION.md
✅ Vídeo tutorial (10min)
✅ Apresentação para stakeholders
✅ Handover para equipe de operação
✅ Definir SLA e procedimentos de emergência
```

**Documentos:**
1. **README.md** - Visão geral do projeto
2. **DEPLOYMENT_GUIDE.md** - Como fazer deploy
3. **ADMIN_GUIDE.md** - Gestão do sistema
4. **USER_MANUAL.md** - Manual do operador
5. **API_DOCUMENTATION.md** - Referência da API
6. **SECURITY.md** - Políticas de segurança
7. **TROUBLESHOOTING.md** - Resolução de problemas

**Apresentação:**
- Funcionalidades entregues
- Métricas de performance
- Custos AWS (real vs estimado)
- Roadmap futuro
- Q&A

**✅ ENTREGA FINAL:** Sistema completo em produção

---

## 📊 Resumo de Entregas

| Semana | Funcionalidades | Arquivos Criados | Testes |
|--------|----------------|------------------|--------|
| **1** | IA Rekognition otimizada | 8 arquivos Python | 4h |
| **2** | Segurança + UI/UX | 12 arquivos (backend + frontend) | 6h |
| **3** | Playback + Recorte | 10 arquivos | 6h |
| **Total** | **Sistema completo** | **30 arquivos** | **16h** |

---

## 💰 Custos Finais

| Item | Custo/mês |
|------|-----------|
| AWS Rekognition (otimizado) | $26 |
| EC2 t3.medium (opcional) | $30 |
| RDS db.t3.small | $25 |
| S3 Storage (100GB gravações) | $2.30 |
| CloudFront (opcional) | $8.50 |
| **Total** | **$91.80/mês** |

**Economia vs não otimizado:** $16.908/mês (99.5%)

---

## 🎯 Métricas de Sucesso

- ✅ Uptime > 99%
- ✅ Latência streaming < 3s
- ✅ Latência playback < 2s
- ✅ Acurácia IA > 85%
- ✅ Custo AWS < $100/mês
- ✅ Zero vulnerabilidades críticas
- ✅ Interface responsiva (mobile + desktop)
- ✅ Tempo de recorte < 30s
- ✅ Documentação completa
- ✅ Equipe treinada

---

## 🚨 Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Custo AWS alto | Baixa | Alto | Motion detection + cooldown |
| Bugs em produção | Média | Médio | Testes automatizados + staging |
| Atraso cronograma | Média | Médio | Buffer de 1 dia por semana |
| Falha segurança | Baixa | Crítico | Auditoria OWASP + penetration test |
| Performance playback | Média | Médio | Testes de carga + otimização ffmpeg |

---

## 📞 Próximos Passos (Pós-MVP)

### **Curto Prazo (1-2 meses):**
- [ ] OCR de placas (EasyOCR) para reduzir custo AWS
- [ ] Notificações em tempo real (WebSocket)
- [ ] Relatórios PDF exportáveis
- [ ] Integração com sistemas externos (API)

### **Médio Prazo (3-6 meses):**
- [ ] Tracking de veículos (DeepSORT)
- [ ] Análise de fluxo de tráfego
- [ ] Heatmaps de detecções
- [ ] Mobile app (React Native)

### **Longo Prazo (6-12 meses):**
- [ ] IA local (YOLO + EasyOCR) para custo zero
- [ ] Edge computing (processamento nas câmeras)
- [ ] Multi-tenant avançado
- [ ] Kubernetes para escala massiva

---

**Última atualização:** 2025-01-15  
**Versão:** 2.0  
**Status:** Pronto para execução  
**Responsável:** Equipe VMS
