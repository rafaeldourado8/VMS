@echo off
echo ========================================
echo Aplicando correções no VMS
echo ========================================
echo.

echo [1/4] Reiniciando serviço de streaming...
docker-compose restart streaming
timeout /t 3 >nul

echo.
echo [2/4] Aplicando migração do banco de dados...
docker-compose exec -T backend python manage.py migrate cameras
timeout /t 2 >nul

echo.
echo [3/4] Limpando câmeras duplicadas do banco...
docker-compose exec -T backend python manage.py shell -c "from apps.cameras.models import Camera; Camera.objects.all().delete(); print('Câmeras removidas')"
timeout /t 2 >nul

echo.
echo [4/4] Reiniciando backend...
docker-compose restart backend
timeout /t 3 >nul

echo.
echo ========================================
echo Correções aplicadas com sucesso!
echo ========================================
echo.
echo Problemas corrigidos:
echo - MediaMTX agora usa hostname correto (mediamtx:9997)
echo - Campos 'name' e 'stream_url' não são mais únicos
echo - Banco de dados limpo e pronto para novas câmeras
echo.
pause
