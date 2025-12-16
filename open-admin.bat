@echo off
echo ========================================
echo Abrindo Django Admin
echo ========================================

echo.
echo Testando conectividade...
echo.

echo [1] Backend direto (porta 8000):
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost:8000/admin/login/

echo.
echo [2] Via Kong (porta 8000):
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost:8000/admin/

echo.
echo [3] Via HAProxy (porta 80):
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost/admin/

echo.
echo ========================================
echo Abrindo navegador...
echo ========================================
start http://localhost:8000/admin/

echo.
echo Se nao abrir, acesse manualmente:
echo - Backend direto: http://localhost:8000/admin/
echo - Via Kong: http://localhost:8000/admin/
echo - Via HAProxy: http://localhost/admin/
pause
