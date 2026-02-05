@echo off
echo Criando stream de teste com FFmpeg...
echo.

REM Publica video de teste no MediaMTX
ffmpeg -re -stream_loop -1 -i 1280_720_60fps.mp4 ^
  -c copy ^
  -f rtsp rtsp://localhost:8554/cam_999

pause
