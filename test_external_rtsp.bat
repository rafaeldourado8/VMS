@echo off
echo ========================================
echo TESTE DE CONECTIVIDADE RTSP EXTERNA
echo ========================================
echo.

echo [1] Verificando IP da maquina...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    set IP=!IP: =!
    echo IP encontrado: !IP!
)

echo.
echo [2] Testando porta RTSP (8554)...
netstat -an | findstr ":8554"

echo.
echo [3] Testando porta API MediaMTX (9997)...
netstat -an | findstr ":9997"

echo.
echo [4] Testando acesso local ao MediaMTX API...
curl -s http://localhost:9997/v3/config/global/get

echo.
echo ========================================
echo CONFIGURACAO PARA MAQUINA DE IA:
echo ========================================
echo.
echo Use este endereco RTSP na maquina de IA:
echo rtsp://SEU_IP_AQUI:8554/NOME_DA_CAMERA
echo.
echo Exemplo:
echo rtsp://192.168.1.100:8554/cam_1
echo.
echo ========================================
pause
