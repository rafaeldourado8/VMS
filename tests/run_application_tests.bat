@echo off
echo === Executando Testes - Application Layer ===
echo.

cd backend
python -m pytest tests/unit/application/ -v --tb=short

echo.
echo === Resumo ===
python -m pytest tests/unit/application/ --tb=no -q

echo.
pause
