@echo off
REM Script para aplicar correção de clips corrompidos e erro 401
REM Reconstrói o container do serviço de clips e reinicia o backend

echo ========================================
echo CORRECAO: CLIPS CORROMPIDOS + ERRO 401
echo ========================================
echo.

echo [1/4] Parando servicos...
docker-compose stop clips backend
if errorlevel 1 (
    echo ERRO: Falha ao parar servicos
    pause
    exit /b 1
)
echo OK
echo.

echo [2/4] Reconstruindo container de clips...
docker-compose build clips
if errorlevel 1 (
    echo ERRO: Falha ao construir container
    pause
    exit /b 1
)
echo OK
echo.

echo [3/4] Iniciando servicos corrigidos...
docker-compose up -d clips backend
if errorlevel 1 (
    echo ERRO: Falha ao iniciar servicos
    pause
    exit /b 1
)
echo OK
echo.

echo [4/4] Aguardando inicializacao...
timeout /t 5 /nobreak >nul
echo OK
echo.

echo ========================================
echo CORRECAO APLICADA COM SUCESSO!
echo ========================================
echo.
echo Verificando status...
docker-compose ps clips backend
echo.

echo ========================================
echo PROXIMOS PASSOS:
echo ========================================
echo.
echo 1. Teste criando um clip pela interface web
echo 2. Ou execute: python scripts\test_clip_creation.py
echo 3. Verifique os logs: docker-compose logs -f clips
echo.
echo Documentacao completa: docs\CLIPS_FIX.md
echo.

pause
