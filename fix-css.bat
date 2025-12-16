@echo off
echo ========================================
echo Corrigindo CSS do Django Admin
echo ========================================

echo.
echo [1/5] Coletando arquivos estaticos...
docker-compose exec -T backend python manage.py collectstatic --noinput --clear

echo.
echo [2/5] Verificando arquivos coletados...
docker-compose exec -T backend sh -c "ls -la /app/staticfiles/admin/css/ | head -10"

echo.
echo [3/5] Verificando volume do Nginx...
docker-compose exec -T nginx sh -c "ls -la /var/www/static/admin/css/ | head -10"

echo.
echo [4/5] Reiniciando servicos...
docker-compose restart backend nginx

echo.
echo [5/5] Aguardando inicializacao (20s)...
timeout /t 20 /nobreak

echo.
echo ========================================
echo Verificando status dos servicos:
echo ========================================
docker-compose ps backend nginx

echo.
echo ========================================
echo CSS corrigido! Acesse:
echo - Admin Django: http://localhost/admin/
echo - API: http://localhost/api/
echo ========================================
echo.
echo IMPORTANTE: Pressione Ctrl+F5 no navegador para limpar cache!
echo.
pause
