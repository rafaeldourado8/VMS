@echo off
REM Script para limpar gravacoes duplicadas do MediaMTX

echo ========================================
echo Limpeza de Gravacoes Duplicadas
echo ========================================
echo.

echo Removendo gravacoes do MediaMTX (formato cam_X)...
if exist "D:\VMS\recordings\cam_1" (
    rmdir /s /q "D:\VMS\recordings\cam_1"
    echo [OK] Removido: cam_1
)

echo.
echo Mantendo apenas gravacoes do Recorder (formato camera_X)
echo.

dir /b "D:\VMS\recordings"

echo.
echo ========================================
echo Limpeza concluida!
echo ========================================
pause
