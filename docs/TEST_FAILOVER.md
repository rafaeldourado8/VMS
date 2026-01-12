# Protocol Failover Test Guide

## Prerequisites
1. Start Docker services:
   ```bash
   docker-compose up -d
   ```

2. Verify services are running:
   ```bash
   docker-compose ps
   ```

## Test Cameras

### Camera 1 - RTSP Intelbras
- **URL**: `rtsp://admin:Camerite123@45.236.226.75:6052/cam/realmonitor?channel=1&subtype=0`
- **Expected Protocol**: HLS (fallback from WebRTC)
- **Indicator**: 📡 Modo Compatível

### Camera 2 - RTSP Hikvision
- **URL**: `rtsp://admin:Camerite@170.84.217.84:603/h264/ch1/main/av_stream`
- **Expected Protocol**: HLS (fallback from WebRTC)
- **Indicator**: 📡 Modo Compatível

### Camera 3 - RTMP
- **URL**: `rtmp://inst-czd17-srs-rtmp-hik-pro-connect.camerite.services:1935/record/FC2487237.stream`
- **Expected Protocol**: RTMP
- **Indicator**: 📺 RTMP

## Manual Test Steps

### 1. Add Cameras via Frontend
1. Open: http://localhost:5173
2. Navigate to "Câmeras" page
3. Click "Adicionar Câmera"
4. Add each camera with the URLs above

### 2. Create Mosaic
1. Navigate to "Mosaicos" page
2. Click "Criar Mosaico"
3. Add all 3 test cameras
4. Click "Visualizar"

### 3. Verify Protocol Indicators
- Check top-right corner of each video player
- Should show:
  - ⚡ Baixa Latência (WebRTC) - initially
  - 📡 Modo Compatível (HLS) - after 5s timeout
  - 📺 RTMP - for RTMP camera

### 4. Check Browser Console
Open DevTools (F12) and look for:
```
Protocol switch: webrtc -> hls
Recording metric: vms_protocol_fallback_total
```

### 5. Verify Metrics
```bash
curl http://localhost:9090/metrics | grep vms_protocol_fallback
```

Expected output:
```
vms_protocol_fallback_total{camera_id="1",from="webrtc",to="hls"} 1
vms_protocol_fallback_total{camera_id="2",from="webrtc",to="hls"} 1
```

## Expected Behavior

### WebRTC → HLS Fallback
1. Player tries WebRTC first
2. After 5s timeout, switches to HLS
3. Indicator changes from ⚡ to 📡
4. After 60s, retries WebRTC

### RTMP Direct
1. Player detects RTMP URL
2. Uses RTMP protocol directly
3. Shows 📺 indicator
4. No fallback needed

## Troubleshooting

### No video showing
- Check MediaMTX logs: `docker-compose logs mediamtx`
- Verify camera URLs are accessible
- Check streaming service: `docker-compose logs streaming`

### Protocol indicator not showing
- Clear browser cache
- Check VideoPlayer component loaded
- Verify protocol state in React DevTools

### Metrics not recording
- Check metrics endpoint: `curl http://localhost:8000/api/metrics`
- Verify metricsClient imported correctly
- Check browser console for errors

## Success Criteria
✅ All 3 cameras show video
✅ Protocol indicators visible
✅ WebRTC → HLS fallback occurs within 5s
✅ RTMP camera shows RTMP indicator
✅ Metrics recorded correctly
✅ WebRTC retry after 60s
