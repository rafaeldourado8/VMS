@echo off
echo ========================================
echo MONITORAMENTO LPR EM TEMPO REAL
echo ========================================
echo.
echo Pressione Ctrl+C para sair
echo.
docker-compose logs -f --tail=100 lpr_service
