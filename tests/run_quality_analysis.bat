@echo off
cls
echo ========================================
echo  VMS - Analise de Qualidade Completa
echo ========================================
echo.
echo Este script executara:
echo  1. Testes unitarios
echo  2. Testes de integracao
echo  3. Analise de complexidade ciclomatica
echo  4. Analise de cobertura
echo.
pause

echo.
echo ========================================
echo  [1/4] TESTES UNITARIOS - DOMAIN
echo ========================================
cd backend
python -m pytest tests/unit/domain/ -v --tb=short
if %errorlevel% neq 0 (
    echo ERRO: Testes de domain falharam!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  [2/4] TESTES UNITARIOS - APPLICATION
echo ========================================
python -m pytest tests/unit/application/ -v --tb=short
if %errorlevel% neq 0 (
    echo ERRO: Testes de application falharam!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  [3/4] TESTES DE INTEGRACAO
echo ========================================
python -m pytest tests/integration/ -v --tb=short
if %errorlevel% neq 0 (
    echo ERRO: Testes de integracao falharam!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  [4/4] ANALISE DE COBERTURA
echo ========================================
python -m pytest tests/ --cov=domain --cov=application --cov=infrastructure --cov-report=term --cov-report=html --cov-fail-under=80

echo.
echo ========================================
echo  RESUMO DE COMPLEXIDADE CICLOMATICA
echo ========================================
radon cc domain/ application/ infrastructure/ -a --total-average

echo.
echo ========================================
echo  ANALISE COMPLETA FINALIZADA!
echo ========================================
echo.
echo Relatorio HTML: backend\htmlcov\index.html
echo.
pause
