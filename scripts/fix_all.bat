@echo off
echo ========================================
echo FIX COMPLETO - Gravacoes Duplicadas
echo ========================================

echo.
echo 1. Parando tudo...
docker-compose down

echo.
echo 2. Limpando gravacoes duplicadas...
rmdir /s /q "D:\VMS\recordings\cam_1" 2>nul
rmdir /s /q "D:\VMS\recordings\cam_2" 2>nul
rmdir /s /q "D:\VMS\recordings\cam_3" 2>nul
rmdir /s /q "D:\VMS\recordings\cam_4" 2>nul
rmdir /s /q "D:\VMS\recordings\cam_5" 2>nul
rmdir /s /q "D:\VMS\recordings\cam_6" 2>nul
rmdir /s /q "D:\VMS\recordings\camera_1\*_*_*" 2>nul
rmdir /s /q "D:\VMS\recordings\camera_2\*_*_*" 2>nul
rmdir /s /q "D:\VMS\recordings\camera_3\*_*_*" 2>nul
rmdir /s /q "D:\VMS\recordings\camera_4\*_*_*" 2>nul
rmdir /s /q "D:\VMS\recordings\camera_5\*_*_*" 2>nul
rmdir /s /q "D:\VMS\recordings\camera_6\*_*_*" 2>nul

echo.
echo 3. Rebuild recorder...
docker-compose build recorder

echo.
echo 4. Subindo servicos...
docker-compose up -d

echo.
echo 5. Aguardando MediaMTX...
timeout /t 20 /nobreak >nul

echo.
echo 6. Desabilitando gravacao no MediaMTX...
docker exec gtvision_mediamtx wget -qO- --post-data="{\"record\":false}" --header="Content-Type: application/json" http://localhost:9997/v3/config/pathdefaults/patch

echo.
echo ========================================
echo CONCLUIDO!
echo Apenas RECORDER grava em camera_X/yyyy-mm-dd/
echo ========================================
pause
