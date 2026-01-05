@echo off
echo === Executando Todos os Testes de Dominio ===
echo.

cd backend
python -m pytest tests/unit/domain/ -v --tb=short

echo.
echo === Resumo ===
python -m pytest tests/unit/domain/ --tb=no -q

echo.
pause
