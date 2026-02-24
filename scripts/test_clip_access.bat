@echo off
REM Testa acesso aos videos dos clips sem autenticacao

echo ========================================
echo TESTE: ACESSO A VIDEOS DE CLIPS
echo ========================================
echo.

echo Aguardando backend inicializar...
timeout /t 3 /nobreak >nul
echo.

echo Testando endpoint de video (deve retornar 404 ou 200, nao 401)...
curl -I http://localhost/api/clips/1/video/ 2>nul
echo.

echo ========================================
echo Se retornou 401: ainda tem problema
echo Se retornou 404: OK (clip nao existe)
echo Se retornou 200: OK (clip existe)
echo ========================================
echo.

pause
