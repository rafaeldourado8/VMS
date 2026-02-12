@echo off
echo ========================================
echo Corrigindo gravacoes duplicadas
echo ========================================
echo.

echo 1. Desabilitando gravacao no MediaMTX...
python scripts\disable_mediamtx_recording.py

echo.
echo 2. Parando servicos...
docker-compose stop recorder recording mediamtx

echo.
echo 3. Removendo gravacoes do MediaMTX (cam_X)...
for /d %%d in ("D:\VMS\recordings\cam_*") do (
    echo Removendo: %%d
    rmdir /s /q "%%d"
)

echo.
echo 4. Removendo gravacoes com formato antigo (dd_mm_yyyy)...
for /d %%d in ("D:\VMS\recordings\camera_*\*_*_*") do (
    echo Removendo: %%d
    rmdir /s /q "%%d"
)

echo.
echo 5. Reiniciando servicos...
docker-compose up -d mediamtx
timeout /t 5 /nobreak >nul
docker-compose up -d streaming recorder recording

echo.
echo 6. Verificando configuracao...
timeout /t 3 /nobreak >nul
python scripts\disable_mediamtx_recording.py

echo.
echo ========================================
echo CONCLUIDO!
echo.
echo Estrutura correta:
echo   camera_X/yyyy-mm-dd/HH-MM-SS.mp4
echo.
echo - RECORDER: Grava
echo - RECORDING: API consulta
echo - MEDIAMTX: NAO grava
echo ========================================
pause
