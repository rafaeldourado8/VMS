# Para o script se qualquer comando falhar
set -e

echo "--- 1. Verificando Formatação (Ruff) ---"
# O '--check' apenas verifica, sem alterar os arquivos
ruff format . --check

echo "--- 2. Verificando Lint (Ruff) ---"
ruff check .

echo "--- 3. Verificando Tipos (MyPy) ---"
mypy .

echo "--- 4. Rodando Testes e Cobertura (Pytest) ---"
# Roda testes (Unitários e Integração) e gera o relatório de cobertura
pytest --cov=. --cov-report=term-missing

echo ""
echo "============================="
echo "=== SUCESSO! Tudo passou! ==="
echo "============================="