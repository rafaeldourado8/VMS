@echo off
echo Adicionando cameras ao MediaMTX...

docker exec gtvision_mediamtx sh -c "echo '{\"source\":\"rtsp://admin:Camerite123@45.236.226.71:6047/cam/realmonitor?channel=1^&subtype=0\",\"sourceOnDemand\":true,\"rtspTransport\":\"tcp\"}' > /tmp/cam1.json && wget --post-file=/tmp/cam1.json --header='Content-Type: application/json' --header='Authorization: Basic bWVkaWFtdHhfYXBpX3VzZXI6R3RWIXNpb25NZWQxYU1UWCQyMDI1' -O- http://localhost:9997/v3/config/paths/add/cam_1"

docker exec gtvision_mediamtx sh -c "echo '{\"source\":\"rtsp://admin:Camerite123@45.236.226.72:6049/cam/realmonitor?channel=1^&subtype=0\",\"sourceOnDemand\":true,\"rtspTransport\":\"tcp\"}' > /tmp/cam2.json && wget --post-file=/tmp/cam2.json --header='Content-Type: application/json' --header='Authorization: Basic bWVkaWFtdHhfYXBpX3VzZXI6R3RWIXNpb25NZWQxYU1UWCQyMDI1' -O- http://localhost:9997/v3/config/paths/add/cam_2"

docker exec gtvision_mediamtx sh -c "echo '{\"source\":\"rtsp://admin:Camerite@186.226.193.111:602/h264/ch1/main/av_stream\",\"sourceOnDemand\":true,\"rtspTransport\":\"tcp\"}' > /tmp/cam3.json && wget --post-file=/tmp/cam3.json --header='Content-Type: application/json' --header='Authorization: Basic bWVkaWFtdHhfYXBpX3VzZXI6R3RWIXNpb25NZWQxYU1UWCQyMDI1' -O- http://localhost:9997/v3/config/paths/add/cam_3"

docker exec gtvision_mediamtx sh -c "echo '{\"source\":\"rtsp://admin:Camerite@170.84.217.84:603/h264/ch1/main/av_stream\",\"sourceOnDemand\":true,\"rtspTransport\":\"tcp\"}' > /tmp/cam4.json && wget --post-file=/tmp/cam4.json --header='Content-Type: application/json' --header='Authorization: Basic bWVkaWFtdHhfYXBpX3VzZXI6R3RWIXNpb25NZWQxYU1UWCQyMDI1' -O- http://localhost:9997/v3/config/paths/add/cam_4"

echo.
echo Cameras adicionadas!
echo Teste: http://localhost/hls/cam_1/index.m3u8
