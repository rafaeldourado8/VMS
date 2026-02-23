@echo off
docker logs gtvision_vod_hls --tail 100 | findstr /C:"FFmpeg stderr"
