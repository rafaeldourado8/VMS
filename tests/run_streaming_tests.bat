@echo off
echo ========================================
echo  Streaming Service - Testes Completos
echo ========================================
echo.

cd services\streaming

echo [1/3] Testes Unitarios - Domain:
echo ----------------------------------
python -m pytest tests/unit/domain/ -v --tb=short

echo.
echo [2/3] Testes Unitarios - Application:
echo --------------------------------------
python -m pytest tests/unit/application/ -v --tb=short

echo.
echo [3/3] Testes de Integracao:
echo ----------------------------
python -m pytest tests/integration/ -v --tb=short

echo.
echo ========================================
echo  Resumo com Cobertura
echo ========================================
python -m pytest tests/ --cov=domain --cov=application --cov=infrastructure --cov-report=term --cov-report=html

echo.
echo Relatorio HTML: services\streaming\htmlcov\index.html
echo.
pause
