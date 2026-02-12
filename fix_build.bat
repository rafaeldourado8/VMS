@echo off
echo Limpando cache corrompido do Docker...

echo.
echo [1/4] Parando containers...
docker-compose down

echo.
echo [2/4] Limpando build cache...
docker builder prune -af

echo.
echo [3/4] Removendo imagens antigas...
docker images | findstr "vms\|gtvision" | for /f "tokens=3" %%i in ('more') do docker rmi -f %%i 2>nul

echo.
echo [4/4] Reconstruindo servicos...
docker-compose build --no-cache --pull

echo.
echo Iniciando servicos...
docker-compose up -d

echo.
echo Concluido! Aguardando inicializacao...
timeout /t 30

docker ps --format "table {{.Names}}\t{{.Status}}"

pause
