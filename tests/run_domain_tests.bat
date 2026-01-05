@echo off
echo === Executando Testes Unitarios - Monitoring Context ===
echo.

cd backend
python -m pytest tests/unit/domain/monitoring/ -v --tb=short

echo.
echo === Testes Concluidos ===
pause
