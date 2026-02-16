@echo off
echo ========================================
echo Teste de Retencao de Gravacoes
echo ========================================
echo.

cd /d "%~dp0..\tests"

echo Criando gravacoes mock...
python test_retention_mock.py

echo.
echo ========================================
echo Teste criado com sucesso!
echo ========================================
echo.
echo Cameras de teste criadas:
echo   - Camera 101: Retencao de 7 dias
echo   - Camera 102: Retencao de 15 dias
echo   - Camera 103: Retencao de 30 dias
echo.
echo Para limpar os dados de teste:
echo   python test_retention_mock.py cleanup
echo.
pause
