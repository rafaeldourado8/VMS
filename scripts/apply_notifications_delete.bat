@echo off
echo Aplicando funcionalidade de apagar notificacoes...

echo Reiniciando backend...
docker-compose restart backend

echo Aguardando backend inicializar...
timeout /t 10

echo Testando endpoints...
curl -X GET http://localhost/api/notifications/logs/ -H "Authorization: Bearer %TOKEN%" 2>nul
if %errorlevel% equ 0 (
    echo ✓ Backend funcionando
) else (
    echo ✗ Erro no backend
)

echo.
echo Funcionalidade de apagar notificacoes aplicada!
echo.
echo Funcionalidades adicionadas:
echo - Apagar notificacao individual (botao lixeira)
echo - Apagar todas as notificacoes (botao "Apagar todas")
echo - Marcar todas como lidas (botao "Marcar todas como lidas")
echo.
pause