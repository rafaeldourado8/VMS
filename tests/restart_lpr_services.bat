@echo off
echo ========================================
echo RESTARTING LPR INTEGRATION SERVICES
echo ========================================

echo.
echo [1/4] Restarting Backend...
docker-compose restart backend

echo.
echo [2/4] Restarting LPR Mercosul...
docker-compose restart lpr_mercosul

echo.
echo [3/4] Restarting MediaMTX...
docker-compose restart mediamtx

echo.
echo [4/4] Waiting for services to be healthy...
timeout /t 10 /nobreak

echo.
echo ========================================
echo CHECKING SERVICE STATUS
echo ========================================

docker-compose ps backend lpr_mercosul mediamtx

echo.
echo ========================================
echo TESTING INTEGRATION
echo ========================================

echo.
echo Testing cameras endpoint...
curl -H "X-API-Key: GtVisionAdmin2025" http://localhost:8000/api/cameras/lpr/active/?protocol=rtsp

echo.
echo.
echo ========================================
echo RESTART COMPLETE
echo ========================================
echo.
echo Next steps:
echo 1. Check logs: docker-compose logs -f lpr_mercosul
echo 2. Run test: python tests\test_lpr_integration.py
echo 3. Check frontend detections
echo.

pause
