@echo off
echo Atualizando Streaming Service com suporte a Snapshot...

echo.
echo [1/3] Parando servico...
docker-compose stop streaming

echo.
echo [2/3] Reconstruindo imagem...
docker-compose build streaming

echo.
echo [3/3] Iniciando servico...
docker-compose up -d streaming

echo.
echo Aguardando servico ficar pronto...
timeout /t 10 /nobreak >nul

echo.
echo Verificando logs...
docker-compose logs --tail=20 streaming

echo.
echo ✓ Concluido! Teste em: http://localhost/streaming/cameras/1/snapshot
pause
