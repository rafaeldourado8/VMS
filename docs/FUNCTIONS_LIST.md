# 📋 VMS v2 - Lista Completa de Funções

## 🎥 1. CÂMERAS

### Backend (Django)
```python
# GET /api/cameras/
def list_cameras(filters: CameraFilters) -> List[Camera]

# GET /api/cameras/{id}/
def get_camera(camera_id: str) -> Camera

# POST /api/cameras/
def create_camera(data: CreateCameraDTO) -> Camera

# PUT /api/cameras/{id}/
def update_camera(camera_id: str, data: UpdateCameraDTO) -> Camera

# DELETE /api/cameras/{id}/
def delete_camera(camera_id: str) -> None

# POST /api/cameras/{id}/activate/
def activate_camera(camera_id: str) -> None

# POST /api/cameras/{id}/deactivate/
def deactivate_camera(camera_id: str) -> None

# GET /api/cameras/{id}/status/
def get_camera_status(camera_id: str) -> CameraStatus

# GET /api/cameras/{id}/thumbnail/
def get_camera_thumbnail(camera_id: str) -> bytes

# POST /api/cameras/{id}/test-connection/
def test_camera_connection(camera_id: str) -> ConnectionResult
```

### Frontend (React)
```typescript
// Hooks
function useGetCameras(filters?: CameraFilters): Camera[]
function useGetCamera(id: string): Camera
function useCreateCamera(): (data: CreateCameraDTO) => Promise<Camera>
function useUpdateCamera(): (id: string, data: UpdateCameraDTO) => Promise<Camera>
function useDeleteCamera(): (id: string) => Promise<void>
function useActivateCamera(): (id: string) => Promise<void>
function useDeactivateCamera(): (id: string) => Promise<void>
function useCameraStatus(id: string): CameraStatus
function useCameraThumbnail(id: string): string
```

---

## 🎬 2. STREAMING

### Backend
```python
# POST /api/streaming/start/
def start_stream(camera_id: str) -> StreamInfo

# POST /api/streaming/stop/
def stop_stream(camera_id: str) -> None

# GET /api/streaming/{camera_id}/url/
def get_stream_url(camera_id: str) -> str

# GET /api/streaming/{camera_id}/status/
def get_stream_status(camera_id: str) -> StreamStatus

# GET /api/streaming/{camera_id}/stats/
def get_stream_stats(camera_id: str) -> StreamStats

# POST /api/streaming/{camera_id}/snapshot/
def capture_snapshot(camera_id: str) -> bytes
```

### Frontend
```typescript
function useStartStream(): (cameraId: string) => Promise<StreamInfo>
function useStopStream(): (cameraId: string) => Promise<void>
function useStreamUrl(cameraId: string): string
function useStreamStatus(cameraId: string): StreamStatus
function useStreamStats(cameraId: string): StreamStats
function useCaptureSnapshot(): (cameraId: string) => Promise<Blob>
```

---

## 🤖 3. DETECÇÕES (LPR)

### Backend
```python
# GET /api/detections/
def list_detections(filters: DetectionFilters) -> PaginatedList[Detection]

# GET /api/detections/{id}/
def get_detection(detection_id: str) -> Detection

# POST /api/detections/search/
def search_detections(query: SearchQuery) -> List[Detection]

# GET /api/detections/stats/
def get_detection_stats(filters: StatsFilters) -> DetectionStats

# GET /api/detections/export/
def export_detections(filters: ExportFilters, format: str) -> bytes

# POST /api/detections/{id}/verify/
def verify_detection(detection_id: str, verified: bool) -> Detection

# POST /api/detections/{id}/correct-plate/
def correct_plate(detection_id: str, correct_plate: str) -> Detection

# DELETE /api/detections/{id}/
def delete_detection(detection_id: str) -> None

# WebSocket
ws://api/detections/live/{camera_id}/
def stream_live_detections(camera_id: str) -> Stream[Detection]
```

### Frontend
```typescript
function useGetDetections(filters?: DetectionFilters): PaginatedList<Detection>
function useGetDetection(id: string): Detection
function useSearchDetections(): (query: SearchQuery) => Promise<Detection[]>
function useDetectionStats(filters?: StatsFilters): DetectionStats
function useExportDetections(): (filters: ExportFilters, format: string) => Promise<Blob>
function useVerifyDetection(): (id: string, verified: boolean) => Promise<Detection>
function useCorrectPlate(): (id: string, plate: string) => Promise<Detection>
function useDeleteDetection(): (id: string) => Promise<void>
function useRealtimeDetections(cameraId: string): Detection[]
```

---

## 💾 4. GRAVAÇÕES

### Backend
```python
# GET /api/recordings/
def list_recordings(filters: RecordingFilters) -> List[Recording]

# GET /api/recordings/{id}/
def get_recording(recording_id: str) -> Recording

# POST /api/recordings/start/
def start_recording(camera_id: str) -> Recording

# POST /api/recordings/stop/
def stop_recording(recording_id: str) -> Recording

# GET /api/recordings/search/
def search_recordings(camera_id: str, start: datetime, end: datetime) -> List[Recording]

# GET /api/recordings/{id}/segments/
def get_recording_segments(recording_id: str) -> List[Segment]

# GET /api/recordings/{id}/download/
def download_recording(recording_id: str) -> bytes

# DELETE /api/recordings/{id}/
def delete_recording(recording_id: str) -> None

# GET /api/recordings/{id}/timeline/
def get_recording_timeline(recording_id: str) -> Timeline
```

### Frontend
```typescript
function useGetRecordings(filters?: RecordingFilters): Recording[]
function useGetRecording(id: string): Recording
function useStartRecording(): (cameraId: string) => Promise<Recording>
function useStopRecording(): (id: string) => Promise<Recording>
function useSearchRecordings(): (cameraId: string, start: Date, end: Date) => Promise<Recording[]>
function useRecordingSegments(id: string): Segment[]
function useDownloadRecording(): (id: string) => Promise<Blob>
function useDeleteRecording(): (id: string) => Promise<void>
function useRecordingTimeline(id: string): Timeline
```

---

## 🎬 5. CLIPES

### Backend
```python
# GET /api/clips/
def list_clips(filters: ClipFilters) -> List[Clip]

# GET /api/clips/{id}/
def get_clip(clip_id: str) -> Clip

# POST /api/clips/
def create_clip(data: CreateClipDTO) -> Clip

# PUT /api/clips/{id}/
def update_clip(clip_id: str, data: UpdateClipDTO) -> Clip

# DELETE /api/clips/{id}/
def delete_clip(clip_id: str) -> None

# GET /api/clips/{id}/download/
def download_clip(clip_id: str) -> bytes

# POST /api/clips/{id}/share/
def share_clip(clip_id: str, expires_in: int) -> ShareLink

# GET /api/clips/shared/{token}/
def get_shared_clip(token: str) -> Clip
```

### Frontend
```typescript
function useGetClips(filters?: ClipFilters): Clip[]
function useGetClip(id: string): Clip
function useCreateClip(): (data: CreateClipDTO) => Promise<Clip>
function useUpdateClip(): (id: string, data: UpdateClipDTO) => Promise<Clip>
function useDeleteClip(): (id: string) => Promise<void>
function useDownloadClip(): (id: string) => Promise<Blob>
function useShareClip(): (id: string, expiresIn: number) => Promise<ShareLink>
function useGetSharedClip(token: string): Clip
```

---

## 🔍 6. BUSCA RETROATIVA (SENTINELA)

### Backend
```python
# POST /api/search/vehicle/
def search_vehicle(query: VehicleSearchQuery) -> SearchJob

# POST /api/search/plate/
def search_plate(plate: str, start: datetime, end: datetime) -> SearchJob

# GET /api/search/jobs/{id}/
def get_search_job(job_id: str) -> SearchJob

# GET /api/search/jobs/{id}/results/
def get_search_results(job_id: str) -> List[SearchResult]

# POST /api/search/jobs/{id}/cancel/
def cancel_search_job(job_id: str) -> None

# GET /api/search/jobs/
def list_search_jobs(filters: JobFilters) -> List[SearchJob]
```

### Frontend
```typescript
function useSearchVehicle(): (query: VehicleSearchQuery) => Promise<SearchJob>
function useSearchPlate(): (plate: string, start: Date, end: Date) => Promise<SearchJob>
function useGetSearchJob(id: string): SearchJob
function useGetSearchResults(id: string): SearchResult[]
function useCancelSearchJob(): (id: string) => Promise<void>
function useListSearchJobs(filters?: JobFilters): SearchJob[]
```

---

## 📊 7. DASHBOARD & ANALYTICS

### Backend
```python
# GET /api/dashboard/overview/
def get_dashboard_overview() -> DashboardOverview

# GET /api/dashboard/detections-by-hour/
def get_detections_by_hour(start: datetime, end: datetime) -> List[HourlyStats]

# GET /api/dashboard/detections-by-camera/
def get_detections_by_camera(start: datetime, end: datetime) -> List[CameraStats]

# GET /api/dashboard/top-plates/
def get_top_plates(start: datetime, end: datetime, limit: int) -> List[PlateStats]

# GET /api/dashboard/detection-confidence/
def get_detection_confidence_distribution() -> ConfidenceDistribution

# GET /api/dashboard/system-health/
def get_system_health() -> SystemHealth
```

### Frontend
```typescript
function useDashboardOverview(): DashboardOverview
function useDetectionsByHour(start: Date, end: Date): HourlyStats[]
function useDetectionsByCamera(start: Date, end: Date): CameraStats[]
function useTopPlates(start: Date, end: Date, limit: number): PlateStats[]
function useDetectionConfidence(): ConfidenceDistribution
function useSystemHealth(): SystemHealth
```

---

## 🚫 8. BLACKLIST

### Backend
```python
# GET /api/blacklist/
def list_blacklist_entries(filters: BlacklistFilters) -> List[BlacklistEntry]

# GET /api/blacklist/{id}/
def get_blacklist_entry(entry_id: str) -> BlacklistEntry

# POST /api/blacklist/
def add_to_blacklist(data: AddBlacklistDTO) -> BlacklistEntry

# PUT /api/blacklist/{id}/
def update_blacklist_entry(entry_id: str, data: UpdateBlacklistDTO) -> BlacklistEntry

# DELETE /api/blacklist/{id}/
def remove_from_blacklist(entry_id: str) -> None

# POST /api/blacklist/import/
def import_blacklist(file: bytes) -> ImportResult

# GET /api/blacklist/export/
def export_blacklist() -> bytes

# GET /api/blacklist/matches/
def get_blacklist_matches(filters: MatchFilters) -> List[BlacklistMatch]
```

### Frontend
```typescript
function useGetBlacklist(filters?: BlacklistFilters): BlacklistEntry[]
function useGetBlacklistEntry(id: string): BlacklistEntry
function useAddToBlacklist(): (data: AddBlacklistDTO) => Promise<BlacklistEntry>
function useUpdateBlacklistEntry(): (id: string, data: UpdateBlacklistDTO) => Promise<BlacklistEntry>
function useRemoveFromBlacklist(): (id: string) => Promise<void>
function useImportBlacklist(): (file: File) => Promise<ImportResult>
function useExportBlacklist(): () => Promise<Blob>
function useBlacklistMatches(filters?: MatchFilters): BlacklistMatch[]
```

---

## 👥 9. USUÁRIOS & AUTENTICAÇÃO

### Backend
```python
# POST /api/auth/login/
def login(email: str, password: str) -> AuthToken

# POST /api/auth/logout/
def logout() -> None

# POST /api/auth/refresh/
def refresh_token(refresh_token: str) -> AuthToken

# POST /api/auth/register/
def register(data: RegisterDTO) -> User

# POST /api/auth/forgot-password/
def forgot_password(email: str) -> None

# POST /api/auth/reset-password/
def reset_password(token: str, new_password: str) -> None

# GET /api/users/me/
def get_current_user() -> User

# PUT /api/users/me/
def update_current_user(data: UpdateUserDTO) -> User

# GET /api/users/
def list_users(filters: UserFilters) -> List[User]

# GET /api/users/{id}/
def get_user(user_id: str) -> User

# POST /api/users/
def create_user(data: CreateUserDTO) -> User

# PUT /api/users/{id}/
def update_user(user_id: str, data: UpdateUserDTO) -> User

# DELETE /api/users/{id}/
def delete_user(user_id: str) -> None

# POST /api/users/{id}/change-password/
def change_user_password(user_id: str, new_password: str) -> None
```

### Frontend
```typescript
function useLogin(): (email: string, password: string) => Promise<AuthToken>
function useLogout(): () => Promise<void>
function useRefreshToken(): (refreshToken: string) => Promise<AuthToken>
function useRegister(): (data: RegisterDTO) => Promise<User>
function useForgotPassword(): (email: string) => Promise<void>
function useResetPassword(): (token: string, password: string) => Promise<void>
function useCurrentUser(): User
function useUpdateCurrentUser(): (data: UpdateUserDTO) => Promise<User>
function useGetUsers(filters?: UserFilters): User[]
function useGetUser(id: string): User
function useCreateUser(): (data: CreateUserDTO) => Promise<User>
function useUpdateUser(): (id: string, data: UpdateUserDTO) => Promise<User>
function useDeleteUser(): (id: string) => Promise<void>
function useChangePassword(): (id: string, password: string) => Promise<void>
```

---

## ⚙️ 10. CONFIGURAÇÕES

### Backend
```python
# GET /api/settings/
def get_settings() -> Settings

# PUT /api/settings/
def update_settings(data: UpdateSettingsDTO) -> Settings

# GET /api/settings/detection/
def get_detection_settings() -> DetectionSettings

# PUT /api/settings/detection/
def update_detection_settings(data: DetectionSettingsDTO) -> DetectionSettings

# GET /api/settings/recording/
def get_recording_settings() -> RecordingSettings

# PUT /api/settings/recording/
def update_recording_settings(data: RecordingSettingsDTO) -> RecordingSettings

# GET /api/settings/notifications/
def get_notification_settings() -> NotificationSettings

# PUT /api/settings/notifications/
def update_notification_settings(data: NotificationSettingsDTO) -> NotificationSettings
```

### Frontend
```typescript
function useGetSettings(): Settings
function useUpdateSettings(): (data: UpdateSettingsDTO) => Promise<Settings>
function useDetectionSettings(): DetectionSettings
function useUpdateDetectionSettings(): (data: DetectionSettingsDTO) => Promise<DetectionSettings>
function useRecordingSettings(): RecordingSettings
function useUpdateRecordingSettings(): (data: RecordingSettingsDTO) => Promise<RecordingSettings>
function useNotificationSettings(): NotificationSettings
function useUpdateNotificationSettings(): (data: NotificationSettingsDTO) => Promise<NotificationSettings>
```

---

## 📈 11. RELATÓRIOS

### Backend
```python
# POST /api/reports/generate/
def generate_report(data: GenerateReportDTO) -> Report

# GET /api/reports/{id}/
def get_report(report_id: str) -> Report

# GET /api/reports/{id}/download/
def download_report(report_id: str, format: str) -> bytes

# GET /api/reports/
def list_reports(filters: ReportFilters) -> List[Report]

# DELETE /api/reports/{id}/
def delete_report(report_id: str) -> None

# GET /api/reports/templates/
def list_report_templates() -> List[ReportTemplate]
```

### Frontend
```typescript
function useGenerateReport(): (data: GenerateReportDTO) => Promise<Report>
function useGetReport(id: string): Report
function useDownloadReport(): (id: string, format: string) => Promise<Blob>
function useListReports(filters?: ReportFilters): Report[]
function useDeleteReport(): (id: string) => Promise<void>
function useReportTemplates(): ReportTemplate[]
```

---

## 🔔 12. NOTIFICAÇÕES

### Backend
```python
# GET /api/notifications/
def list_notifications(filters: NotificationFilters) -> List[Notification]

# GET /api/notifications/{id}/
def get_notification(notification_id: str) -> Notification

# POST /api/notifications/{id}/read/
def mark_notification_read(notification_id: str) -> Notification

# POST /api/notifications/read-all/
def mark_all_notifications_read() -> None

# DELETE /api/notifications/{id}/
def delete_notification(notification_id: str) -> None

# WebSocket
ws://api/notifications/live/
def stream_live_notifications() -> Stream[Notification]
```

### Frontend
```typescript
function useGetNotifications(filters?: NotificationFilters): Notification[]
function useGetNotification(id: string): Notification
function useMarkNotificationRead(): (id: string) => Promise<Notification>
function useMarkAllNotificationsRead(): () => Promise<void>
function useDeleteNotification(): (id: string) => Promise<void>
function useRealtimeNotifications(): Notification[]
```

---

## 🏥 13. SISTEMA & MONITORAMENTO

### Backend
```python
# GET /api/health/
def health_check() -> HealthStatus

# GET /api/metrics/
def get_metrics() -> Metrics

# GET /api/system/info/
def get_system_info() -> SystemInfo

# GET /api/system/logs/
def get_system_logs(filters: LogFilters) -> List[LogEntry]

# POST /api/system/restart-service/
def restart_service(service_name: str) -> None

# GET /api/system/storage/
def get_storage_info() -> StorageInfo

# POST /api/system/cleanup/
def cleanup_old_data(days: int) -> CleanupResult
```

### Frontend
```typescript
function useHealthCheck(): HealthStatus
function useMetrics(): Metrics
function useSystemInfo(): SystemInfo
function useSystemLogs(filters?: LogFilters): LogEntry[]
function useRestartService(): (serviceName: string) => Promise<void>
function useStorageInfo(): StorageInfo
function useCleanupOldData(): (days: number) => Promise<CleanupResult>
```

---

## 📊 RESUMO TOTAL

### Backend Endpoints
```
Câmeras:           10 endpoints
Streaming:         6 endpoints
Detecções:         9 endpoints
Gravações:         9 endpoints
Clipes:            8 endpoints
Busca Retroativa:  6 endpoints
Dashboard:         6 endpoints
Blacklist:         8 endpoints
Usuários:          14 endpoints
Configurações:     8 endpoints
Relatórios:        6 endpoints
Notificações:      6 endpoints
Sistema:           7 endpoints
─────────────────────────────
TOTAL:             103 endpoints
```

### Frontend Hooks
```
Câmeras:           9 hooks
Streaming:         6 hooks
Detecções:         9 hooks
Gravações:         9 hooks
Clipes:            8 hooks
Busca Retroativa:  6 hooks
Dashboard:         6 hooks
Blacklist:         8 hooks
Usuários:          14 hooks
Configurações:     8 hooks
Relatórios:        6 hooks
Notificações:      6 hooks
Sistema:           7 hooks
─────────────────────────────
TOTAL:             102 hooks
```

---

## 🎯 MVP Mínimo (30 dias)

### Essenciais (Obrigatório)
```
✓ Câmeras: CRUD + Status
✓ Streaming: Start/Stop + URL
✓ Detecções: List + Search + Stats
✓ Gravações: Start/Stop + Search
✓ Usuários: Login + CRUD
✓ Dashboard: Overview + Stats
```

### Nice-to-Have (Opcional)
```
○ Clipes permanentes
○ Busca retroativa
○ Blacklist
○ Relatórios
○ Notificações avançadas
```

---

**Total de Funções:** ~200  
**MVP Mínimo:** ~60 funções  
**Tempo Estimado:** 30 dias (10h/dia)
