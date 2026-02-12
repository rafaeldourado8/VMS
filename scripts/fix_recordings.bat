@echo off
echo Corrigindo gravacoes duplicadas...
echo.

echo 1. Parando servicos...
docker-compose stop recorder recording mediamtx

echo.
echo 2. Removendo gravacoes do MediaMTX (cam_X)...
for /d %%d in ("D:\VMS\recordings\cam_*") do (
    echo Removendo: %%d
    rmdir /s /q "%%d"
)

echo.
echo 3. Removendo gravacoes com formato antigo (dd_mm_yyyy)...
for /d %%d in ("D:\VMS\recordings\camera_*\*_*_*") do (
    echo Removendo: %%d
    rmdir /s /q "%%d"
)

echo.
echo 4. Reiniciando servicos...
docker-compose up -d recorder recording mediamtx

echo.
echo ========================================
echo Estrutura correta:
echo   camera_X/yyyy-mm-dd/HH-MM-SS.mp4
echo.
echo Apenas RECORDER grava
echo Recording service apenas consulta
echo MediaMTX NAO grava
echo ========================================
pause
