# VMS Implementation Tasks

**Status**: 12 câmeras streaming ✅ | AI 50% | Recording ❌ | Security 40%

---

## 🔥 PHASE 1: FIX AI (1-2 days)

### Task 1.1: Fix Dependencies
- [x] Edit `services/ai_detection/requirements.txt`
  - Change: `typing-extensions>=4.8.0`
  - Change: `opencv-python-headless==4.8.1.78`
- [x] Rebuild: `docker-compose build --no-cache ai_worker_1 ai_worker_2`

### Task 1.2: Fix RabbitMQ Permissions
- [x] Edit `docker-compose.yml`
  - Add volume: `- ./config/rabbitmq/.erlang.cookie:/var/lib/rabbitmq/.erlang.cookie:ro`
- [x] Create `config/rabbitmq/.erlang.cookie` (chmod 400)
- [x] Restart: `docker-compose up -d rabbitmq_ai`

### Task 1.3: Frame Ingestion
- [ ] Create `services/ai_detection/infrastructure/frame_extractor.py`
  - FFmpeg RTSP → JPEG (1 FPS)
  - Publish to RabbitMQ queue
- [ ] Test: Verify frames in queue

### Task 1.4: Rekognition Adapter
- [ ] Create `services/ai_detection/infrastructure/providers/rekognition.py`
  - Implement `DetectionProvider` protocol
  - DetectLabels + DetectFaces
  - Timeout: 5s, Retry: 3x
- [ ] Test: Mock AWS call

### Task 1.5: Event Normalization
- [ ] Edit `services/ai_detection/domain/detection_result.py`
  - Normalize to `DetectionResult` schema
  - Add timestamp, camera_id, provider
- [ ] Persist to PostgreSQL
- [ ] Publish to RabbitMQ `detections` exchange

### Task 1.6: Cost Tracking
- [ ] Create `services/ai_detection/application/cost_tracker.py`
  - Track calls per camera
  - Calculate cost (DetectLabels: $0.001, DetectFaces: $0.001)
- [ ] Add metric: `vms_rekognition_cost_usd{camera_id}`

**Acceptance**: AI service starts, frames processed, results in DB

---

## 📹 PHASE 2: RECORDING & PLAYBACK (3-5 days)

### Task 2.1: Storage Structure
- [ ] Create `services/recorder/storage.py`
  - Path: `/{camera_id}/{yyyy}/{mm}/{dd}/{hh}/segment_{timestamp}.mp4`
  - Retention config: 7/15/30 days
- [ ] Create storage directory: `/mnt/vms/recordings/`

### Task 2.2: Recorder Service
- [ ] Create `services/recorder/main.py`
  - FastAPI service
  - Endpoint: POST /record/start, /record/stop
- [ ] Create `services/recorder/ffmpeg_recorder.py`
  - Input: `rtsp://mediamtx:8554/camera/{id}`
  - Output: MP4 segments (1-5 min)
  - Filename: `{camera_id}_{timestamp}.mp4`
- [ ] Add to `docker-compose.yml`

### Task 2.3: Cleanup Job
- [ ] Create `services/recorder/cleanup.py`
  - Cron: daily at 2 AM
  - Delete files older than retention
- [ ] Add to `docker-compose.yml` as cron service

### Task 2.4: Playback API (Backend)
- [ ] Create `backend/apps/playback/` Django app
- [ ] Create `backend/domain/playback/recording.py`
  - Entity: Recording (camera_id, start, end, path)
- [ ] Create `backend/apps/playback/views.py`
  - GET `/api/playback/{camera_id}?start=ISO&end=ISO`
  - Return: MP4 URL or HLS playlist
- [ ] Create `backend/infrastructure/persistence/recording_repository.py`

### Task 2.5: Timeline UI
- [ ] Create `frontend/src/components/Timeline.tsx`
  - Canvas-based timeline
  - Show recording segments
  - Seek to timestamp
- [ ] Create `frontend/src/components/PlaybackPlayer.tsx`
  - Video.js player
  - Load MP4 from API
- [ ] Add to camera detail page

**Acceptance**: Record 5 min, playback works, timeline shows segments

---

## 🔐 PHASE 3: SECURITY (3-5 days)

### Task 3.1: JWT Generation
- [ ] Create `backend/infrastructure/auth/jwt_service.py`
  - Generate JWT with 1h expiry
  - Claims: `camera_id`, `tenant_id`, `permissions`
  - Secret from env: `JWT_SECRET`
- [ ] Add endpoint: POST `/api/auth/stream-token`

### Task 3.2: Redis Blacklist
- [ ] Create `backend/infrastructure/auth/blacklist.py`
  - Add token to Redis on revoke
  - Check blacklist on validation
- [ ] Add endpoint: POST `/api/auth/revoke`

### Task 3.3: Kong Rate Limiting
- [ ] Edit `kong/kong.yml`
  - Add plugin: `rate-limiting`
  - Config: 100 req/min per consumer
- [ ] Test: Exceed limit, verify 429

### Task 3.4: JWT Validation MediaMTX
- [ ] Edit `mediamtx.yml`
  - Add `authHTTPAddress: http://backend:8000/api/auth/validate-stream`
- [ ] Create `backend/apps/cameras/views.py`
  - POST `/api/auth/validate-stream`
  - Validate JWT, check camera_id claim
  - Return 200 or 401

### Task 3.5: RBAC Implementation
- [ ] Edit `backend/apps/usuarios/permissions.py`
  - Roles: `viewer`, `operator`, `admin`
  - Permissions: `view_stream`, `control_camera`, `manage_config`
- [ ] Apply to all endpoints with `@permission_required`

### Task 3.6: Audit Log
- [ ] Create `backend/apps/audit/models.py`
  - Fields: user, action, resource, timestamp, ip
- [ ] Create middleware: `backend/infrastructure/auth/audit_middleware.py`
  - Log all POST/PUT/DELETE requests
- [ ] Add to `MIDDLEWARE` in settings

### Task 3.7: AWS Secrets Manager
- [ ] Create `terraform/modules/secrets/main.tf`
  - Store: DB password, JWT secret, AWS keys
- [ ] Edit services to read from Secrets Manager
- [ ] Remove secrets from `.env`

### Task 3.8: TLS Internal
- [ ] Generate certs: `scripts/generate_certs.sh`
- [ ] Edit `docker-compose.yml`
  - Mount certs to all services
  - Update URLs to https://
- [ ] Test: Verify TLS handshake

**Acceptance**: JWT auth works, rate limit active, audit log captures actions

---

## 🔔 PHASE 4: EVENTS & ORCHESTRATION (2-3 days)

### Task 4.1: RabbitMQ Exchanges
- [ ] Create `config/rabbitmq/definitions.json`
  - Exchange: `detections` (topic)
  - Exchange: `alerts` (fanout)
  - Queue: `detections.processing`
  - Queue: `alerts.notifications`
- [ ] Edit `docker-compose.yml`
  - Mount definitions to RabbitMQ
  - Env: `RABBITMQ_DEFINITIONS=/etc/rabbitmq/definitions.json`

### Task 4.2: DLQ Configuration
- [ ] Edit `config/rabbitmq/definitions.json`
  - Queue: `detections.dlq`
  - Queue: `alerts.dlq`
  - Bind with `x-dead-letter-exchange`
- [ ] Set TTL: 24h on DLQ

### Task 4.3: Celery Consumer
- [ ] Create `backend/infrastructure/messaging/celery_consumer.py`
  - Task: `process_detection_event`
  - Consume from `detections.processing`
  - Persist to `detection_results` table
- [ ] Edit `backend/config/celery.py`
  - Register task
  - Set broker: RabbitMQ

### Task 4.4: Retry Logic
- [ ] Edit `backend/infrastructure/messaging/celery_consumer.py`
  - Add `@task(bind=True, max_retries=3)`
  - Exponential backoff: 2^retry seconds
- [ ] Test: Simulate failure, verify retries

### Task 4.5: WebSocket Push
- [ ] Create `backend/infrastructure/messaging/websocket.py`
  - Django Channels consumer
  - Subscribe to `detections` exchange
- [ ] Create `backend/apps/dashboard/consumers.py`
  - Push to WebSocket on new detection
- [ ] Edit `frontend/src/hooks/useDetections.ts`
  - Connect to WebSocket
  - Update state on message

**Acceptance**: Detection event → Celery → DB → WebSocket → Dashboard

---

## 📊 PHASE 5: OBSERVABILITY (2-3 days)

### Task 5.1: Prometheus Metrics
- [ ] Create `config/prometheus/prometheus.yml`
  - Scrape: streaming:8001, ai:8002, backend:8000
- [ ] Add to `docker-compose.yml`
- [ ] Create `services/streaming/infrastructure/metrics.py`
  - Metrics: `vms_streams_active`, `vms_webrtc_latency_ms`
- [ ] Create `services/ai_detection/infrastructure/metrics.py`
  - Metrics: `vms_rekognition_calls`, `vms_rekognition_cost_usd`
- [ ] Create `backend/infrastructure/metrics.py`
  - Metrics: `vms_api_requests`, `vms_storage_bytes`

### Task 5.2: Structured Logging
- [ ] Edit all services `main.py`
  - Use `structlog` or `python-json-logger`
  - Format: `{"service": "streaming", "level": "INFO", "message": "...", "trace_id": "...", "camera_id": "..."}`
- [ ] Add `trace_id` to all requests (middleware)

### Task 5.3: Alertmanager Rules
- [ ] Create `config/prometheus/alerts.yml`
  - Alert: `StreamOffline` (no frames > 60s)
  - Alert: `StorageCritical` (disk > 90%)
  - Alert: `AICostAnomaly` (daily cost > threshold)
- [ ] Add Alertmanager to `docker-compose.yml`
- [ ] Configure webhook to Slack/email

### Task 5.4: Grafana Dashboards
- [ ] Create `config/grafana/dashboards/vms.json`
  - Panel: Active streams per camera
  - Panel: WebRTC latency
  - Panel: AI cost per camera
  - Panel: Storage usage
- [ ] Add Grafana to `docker-compose.yml`
- [ ] Import dashboard

**Acceptance**: Metrics visible, logs structured, alerts firing, dashboard operational

---

## ⚡ PHASE 6: TESTS (3-5 days)

### Task 6.1: Streaming Tests
- [ ] Create `services/streaming/tests/test_resilience.py`
  - `test_camera_disconnect_reconnect`
  - `test_webrtc_fallback_to_hls`
  - `test_stream_recovery_after_mediamtx_restart`
- [ ] Create `services/streaming/tests/test_auth.py`
  - `test_jwt_expiry_rejection`
  - `test_invalid_token_rejection`

### Task 6.2: AI Tests
- [ ] Create `services/ai_detection/tests/test_providers.py`
  - `test_provider_interface_compliance`
  - `test_rekognition_timeout_handling`
  - `test_detection_false_positive_rate`
- [ ] Create `services/ai_detection/tests/test_cost.py`
  - `test_cost_tracking_accuracy`

### Task 6.3: Playback Tests
- [ ] Create `backend/tests/integration/test_playback.py`
  - `test_gap_in_recording`
  - `test_corrupted_segment_skip`
  - `test_time_range_query`
  - `test_concurrent_playback`

### Task 6.4: E2E Tests
- [ ] Create `tests_integration/test_e2e.py`
  - `test_full_user_flow_live_to_playback`
  - `test_detection_to_alert_flow`
  - `test_multi_camera_streaming`

**Acceptance**: All tests pass, coverage > 80%

---

## 🚀 PHASE 7: SCALE & PRODUCTION (5-7 days)

### Task 7.1: AI Backpressure
- [ ] Edit `services/ai_detection/infrastructure/queue.py`
  - Check queue size before publish
  - Drop frame if queue > 1000
  - Log dropped frames

### Task 7.2: HAProxy Camera Hash
- [ ] Edit `haproxy/haproxy.cfg`
  - Add `balance hdr(X-Camera-ID)`
  - Route by camera_id hash

### Task 7.3: MediaMTX Horizontal Scaling
- [ ] Edit `docker-compose.yml`
  - Add `mediamtx_2`, `mediamtx_3`
  - Max 50 streams per instance
- [ ] Edit HAProxy to load balance

### Task 7.4: Storage Tiering
- [ ] Create `services/recorder/tiering.py`
  - Cron: daily
  - Move files > 7 days to S3
  - Delete from local SSD
- [ ] Add S3 bucket in Terraform

### Task 7.5: Tenant Isolation
- [ ] Edit `mediamtx.yml`
  - Path pattern: `/{tenant_id}/camera/{id}`
- [ ] Edit all services to include tenant_id

### Task 7.6: Healthchecks
- [ ] Add `/health` endpoint to all services
  - Check: DB connection, Redis, RabbitMQ
  - Return: 200 or 503

### Task 7.7: Frontend Build Optimization
- [ ] Edit `frontend/vite.config.ts`
  - Enable code splitting
  - Lazy load routes
  - Compress assets
- [ ] Target: < 2MB gzipped

### Task 7.8: Kubernetes Manifests
- [ ] Create `k8s/base/`
  - Deployment: streaming, ai, backend, frontend
  - Service: ClusterIP for internal, LoadBalancer for frontend
  - ConfigMap: env vars
  - Secret: credentials
- [ ] Create `k8s/overlays/prod/`
  - Replicas: streaming=3, ai=5, backend=3
  - Resources: CPU/memory limits

### Task 7.9: Blue-Green Deployment
- [ ] Create `k8s/base/deployment-blue.yaml`
- [ ] Create `k8s/base/deployment-green.yaml`
- [ ] Create `scripts/deploy.sh`
  - Deploy green
  - Run smoke tests
  - Switch traffic
  - Delete blue

### Task 7.10: Documentation
- [ ] Create `docs/architecture/DIAGRAM.md`
  - Mermaid diagram of full system
- [ ] Create `docs/runbook/OPERATIONS.md`
  - Incident response procedures
  - Common issues and fixes
- [ ] Update `README.md`
  - Quick start guide
  - Architecture overview

**Acceptance**: System scales to 100 cameras, K8s deployment works, docs complete

---

## 📋 QUICK REFERENCE

### Current Status
```
✅ Streaming:     90% (12 cameras working)
⚠️  AI:           50% (domain done, service broken)
❌ Recording:     0%
⚠️  Security:     40% (basic auth only)
⚠️  Events:       30% (RabbitMQ exists, no consumers)
❌ Observability: 20% (basic logs only)
❌ Scale:         0%
⚠️  Tests:        40% (unit tests only)
⚠️  Production:   50% (Docker only, no K8s)
```

### Priority Order
1. **Phase 1** (AI) - Unblock detection features
2. **Phase 2** (Recording) - Core VMS feature
3. **Phase 3** (Security) - Production requirement
4. **Phase 4** (Events) - Enable real-time features
5. **Phase 5** (Observability) - Production requirement
6. **Phase 6** (Tests) - Quality assurance
7. **Phase 7** (Scale) - Production readiness

### Estimated Timeline
- **Minimum Viable**: Phases 1-3 (7-12 days)
- **Production Ready**: Phases 1-5 (14-22 days)
- **Enterprise Ready**: All phases (19-30 days)

### Dependencies
```
Phase 1 (AI) → Phase 4 (Events)
Phase 2 (Recording) → Phase 6 (Tests)
Phase 3 (Security) → Phase 1 (AI), Phase 7 (Scale)
Phase 5 (Observability) → Phase 7 (Scale)
Phase 6 (Tests) → Phase 7 (Production)
```

---

**Next Action**: Choose phase to start → Execute tasks → Update checkboxes
