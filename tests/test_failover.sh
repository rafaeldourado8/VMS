#!/bin/bash
# Test Protocol Failover with Real Cameras

echo "🧪 Testing Protocol Failover"
echo "=============================="

# Backend URL
BACKEND_URL="http://localhost:8000"

# Test cameras
declare -a CAMERAS=(
  "1|rtsp://admin:Camerite123@45.236.226.75:6052/cam/realmonitor?channel=1&subtype=0|Camera RTSP 1"
  "2|rtsp://admin:Camerite@170.84.217.84:603/h264/ch1/main/av_stream|Camera RTSP 2"
  "3|rtmp://inst-czd17-srs-rtmp-hik-pro-connect.camerite.services:1935/record/FC2487237.stream|Camera RTMP"
)

echo ""
echo "📹 Provisioning cameras..."
for camera in "${CAMERAS[@]}"; do
  IFS='|' read -r id url name <<< "$camera"
  
  echo "  → Camera $id: $name"
  
  response=$(curl -s -X POST "$BACKEND_URL/api/cameras/" \
    -H "Content-Type: application/json" \
    -d "{
      \"name\": \"$name\",
      \"rtsp_url\": \"$url\",
      \"location\": \"Test Location\",
      \"status\": \"online\"
    }")
  
  echo "     Response: $response"
done

echo ""
echo "⏳ Waiting 10s for streams to initialize..."
sleep 10

echo ""
echo "🔍 Checking stream status..."
for camera in "${CAMERAS[@]}"; do
  IFS='|' read -r id url name <<< "$camera"
  
  echo "  → Camera $id:"
  
  status=$(curl -s "$BACKEND_URL/api/cameras/$id/stream")
  echo "     $status"
done

echo ""
echo "✅ Test complete!"
echo ""
echo "📊 Next steps:"
echo "  1. Open frontend: http://localhost:5173"
echo "  2. Navigate to Mosaicos page"
echo "  3. Create mosaic with test cameras"
echo "  4. Observe protocol indicators:"
echo "     - ⚡ Baixa Latência (WebRTC)"
echo "     - 📡 Modo Compatível (HLS)"
echo "     - 📺 RTMP"
echo "  5. Check browser console for protocol switches"
echo "  6. Monitor metrics: curl http://localhost:9090/metrics | grep vms_protocol_fallback"
