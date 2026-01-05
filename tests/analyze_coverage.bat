@echo off
echo ========================================
echo  Analise de Cobertura de Testes
echo ========================================
echo.

cd backend

echo Executando testes com cobertura...
echo.

python -m pytest tests/ -v --cov=domain --cov=application --cov=infrastructure --cov-report=term-missing --cov-report=html

echo.
echo ========================================
echo  Relatorio HTML gerado em:
echo  backend/htmlcov/index.html
echo ========================================
echo.

pause
