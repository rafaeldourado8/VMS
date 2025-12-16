@echo off
echo ========================================
echo Verificando Arquivos Estaticos
echo ========================================

echo.
echo [1] Verificando collectstatic no backend...
docker-compose exec -T backend sh -c "if [ -d /app/staticfiles/admin ]; then echo 'OK: Arquivos estaticos existem'; else echo 'ERRO: Arquivos estaticos NAO encontrados'; fi"

echo.
echo [2] Contando arquivos CSS do admin...
docker-compose exec -T backend sh -c "find /app/staticfiles/admin/css -name '*.css' 2>/dev/null | wc -l"

echo.
echo [3] Verificando volume do Nginx...
docker-compose exec -T nginx sh -c "if [ -d /var/www/static/admin ]; then echo 'OK: Nginx tem acesso aos arquivos'; else echo 'ERRO: Nginx NAO tem acesso'; fi"

echo.
echo [4] Testando acesso HTTP ao CSS...
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost/static/admin/css/base.css

echo.
echo [5] Verificando logs recentes do backend...
docker-compose logs --tail=5 backend | findstr /i "static"

echo.
echo [6] Status dos containers...
docker-compose ps backend nginx

echo.
echo ========================================
echo Diagnostico completo!
echo ========================================
echo.
echo Se encontrou erros, execute: fix-css.bat
pause
