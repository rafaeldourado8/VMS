@echo off
echo ========================================
echo FIXAR IP PARA 192.168.0.102
echo ========================================
echo.
echo ATENCAO: Execute como Administrador!
echo.
echo Este script vai configurar o IP fixo 192.168.0.102
echo na interface Wi-Fi
echo.
pause

netsh interface ip set address name="Wi-Fi" static 192.168.0.102 255.255.255.0 192.168.0.1

echo.
echo IP configurado para 192.168.0.102
echo.
echo Verificando...
ipconfig | findstr "192.168.0.102"
echo.
pause
