# 🎯 MVP Roadmap - Remaining Work

**Current Status:** Sprint 4 COMPLETO  
**MVP Completion:** 40% (4/10 sprints)  
**Estimated Time:** 21 dias restantes

---

## ✅ Completed (40%)

### Sprint 0: Base (21 dias) - COMPLETO
- ✅ Cidades (multi-tenant)
- ✅ Cameras (auto-detection)
- ✅ Streaming (MediaMTX)
- ✅ LPR (detection stub)

### Sprint 4: Admin + Auth (3 dias) - COMPLETO
- ✅ User entity
- ✅ Permission system
- ✅ Authentication use cases
- ✅ 21 tests, 97% coverage

---

## 🚀 Remaining Work (60%)

### Sprint 5: Integration + FastAPI (7 dias)

#### Infrastructure Layer
```python
# 1. JWT Service (1 dia)
class JWTService:
    def generate_token(self, payload: dict) -> str
    def verify_token(self, token: str) -> dict
    def refresh_token(self, token: str) -> str
```

#### FastAPI Endpoints (2 dias)
```python
POST /api/auth/register
POST /api/auth/login
GET /api/auth/me
PUT /api/auth/permissions/{user_id}
POST /api/auth/refresh
```

#### Middleware (1 dia)
```python
@app.middleware("http")
async def authenticate_request(request, call_next):
    # Verify JWT token
    # Inject user into request
```

#### Django Integration (2 dias)
```python
# UserModel
# Admin interface
# Migrations
```

#### Tests (1 dia)
- Integration tests
- API tests
- End-to-end tests

---

### Sprint 6: YOLO Real + Recording (7 dias)

#### YOLO Real Implementation (3 dias)
```python
# 1. Train YOLO model
# 2. Replace stub provider
# 3. Test with real cameras
```

#### Recording Service (3 dias)
```python
# 1. Cyclic recording
# 2. Clip creation
# 3. Storage management
```

#### Tests (1 dia)
- YOLO accuracy tests
- Recording tests
- Storage tests

---

### Sprint 7: Deploy + Monitoring (7 dias)

#### Docker Compose (2 dias)
```yaml
services:
  - postgres
  - redis
  - rabbitmq
  - mediamtx
  - backend
  - frontend
  - lpr_detection
```

#### Monitoring (2 dias)
```python
# Prometheus metrics
# Grafana dashboards
# Alerting rules
```

#### Documentation (2 dias)
- Deployment guide
- API documentation
- User manual

#### Final Tests (1 dia)
- Load testing
- Security testing
- UAT

---

## 📊 Detailed Breakdown

### Sprint 5: Integration + FastAPI

#### Day 1: JWT Service
- [ ] Install PyJWT
- [ ] Implement JWTService
- [ ] Add RS256 keys
- [ ] Test token generation
- [ ] Test token verification

#### Day 2-3: FastAPI Endpoints
- [ ] Create auth router
- [ ] POST /auth/register
- [ ] POST /auth/login
- [ ] GET /auth/me
- [ ] PUT /auth/permissions
- [ ] POST /auth/refresh

#### Day 4: Middleware
- [ ] Create JWT middleware
- [ ] Add to FastAPI app
- [ ] Test authentication
- [ ] Test authorization

#### Day 5-6: Django Integration
- [ ] Create UserModel
- [ ] Create migrations
- [ ] Create admin interface
- [ ] Test CRUD operations

#### Day 7: Tests
- [ ] Integration tests
- [ ] API tests
- [ ] Coverage > 90%

---

### Sprint 6: YOLO Real + Recording

#### Day 1-3: YOLO Real
- [ ] Collect training data
- [ ] Train YOLOv8n model
- [ ] Replace stub provider
- [ ] Test accuracy
- [ ] Optimize performance

#### Day 4-6: Recording
- [ ] Implement recording service
- [ ] Cyclic storage logic
- [ ] Clip creation
- [ ] Notification system
- [ ] Storage cleanup

#### Day 7: Tests
- [ ] YOLO accuracy tests
- [ ] Recording tests
- [ ] Storage tests

---

### Sprint 7: Deploy + Monitoring

#### Day 1-2: Docker Compose
- [ ] Create docker-compose.yml
- [ ] Configure services
- [ ] Test deployment
- [ ] Optimize resources

#### Day 3-4: Monitoring
- [ ] Setup Prometheus
- [ ] Create Grafana dashboards
- [ ] Add alerting rules
- [ ] Test monitoring

#### Day 5-6: Documentation
- [ ] Deployment guide
- [ ] API documentation
- [ ] User manual
- [ ] Troubleshooting guide

#### Day 7: Final Tests
- [ ] Load testing
- [ ] Security testing
- [ ] UAT
- [ ] Bug fixes

---

## 🎯 MVP Deliverables

### Core Features
- ✅ Multi-tenant (1 DB per city)
- ✅ Camera management (RTSP + RTMP)
- ✅ HLS streaming
- ✅ LPR detection (stub)
- ✅ User authentication
- ⏳ JWT authorization
- ⏳ YOLO real detection
- ⏳ Recording + playback
- ⏳ Docker deployment

### Quality Metrics
- ✅ 88 tests (target: 150+)
- ✅ 97% coverage (target: 90%+)
- ✅ Complexity A (target: A/B)
- ⏳ API documentation
- ⏳ Deployment guide

---

## 📅 Timeline

```
Week 1 (Sprint 5): Integration + FastAPI
├── Day 1: JWT Service
├── Day 2-3: FastAPI Endpoints
├── Day 4: Middleware
├── Day 5-6: Django Integration
└── Day 7: Tests

Week 2 (Sprint 6): YOLO Real + Recording
├── Day 1-3: YOLO Real
├── Day 4-6: Recording Service
└── Day 7: Tests

Week 3 (Sprint 7): Deploy + Monitoring
├── Day 1-2: Docker Compose
├── Day 3-4: Monitoring
├── Day 5-6: Documentation
└── Day 7: Final Tests

Total: 21 days
```

---

## 🚧 Blockers & Risks

### High Priority
- 🔴 YOLO model training (requires labeled data)
- 🔴 Real cameras for testing
- 🔴 Production server for deployment

### Medium Priority
- 🟡 JWT key management
- 🟡 Storage capacity planning
- 🟡 Network bandwidth testing

### Low Priority
- 🔵 Performance optimization
- 🔵 UI/UX improvements
- 🔵 Mobile app

---

## 💰 Cost Estimate

### Development
- Sprint 5: 7 dias × $500/dia = $3,500
- Sprint 6: 7 dias × $500/dia = $3,500
- Sprint 7: 7 dias × $500/dia = $3,500
- **Total:** $10,500

### Infrastructure (Monthly)
- Banda: $5,000
- CPU: $500
- Storage: $250
- **Total:** $5,750/mês

---

## ✅ Success Criteria

### Functional
- [ ] 1000 cameras per city
- [ ] 20 LPR cameras active
- [ ] Real-time detection
- [ ] 7/15/30 days recording
- [ ] Multi-tenant working

### Non-Functional
- [ ] 99% uptime
- [ ] < 2s latency
- [ ] 90%+ test coverage
- [ ] < 5% error rate
- [ ] Documented APIs

---

## 🎓 Post-MVP

### Phase 2: Sentinela
- Retroactive search
- AWS Rekognition
- Video analysis
- Timeline view

### Phase 3: Analytics
- Detection reports
- Traffic analysis
- Heatmaps
- Dashboards

### Phase 4: Mobile
- iOS app
- Android app
- Push notifications
- Offline mode

---

**Next Action:** Start Sprint 5 - Integration + FastAPI

**Estimated MVP Completion:** 21 dias
