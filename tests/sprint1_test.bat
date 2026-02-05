@echo off
echo Copiando script para container...
docker cp tests\validate_inside.py gtvision_mediamtx:/tmp/validate.py

echo.
echo Executando validacao...
docker exec gtvision_mediamtx python3 /tmp/validate.py

echo.
pause
