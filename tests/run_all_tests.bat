@echo off
echo ========================================
echo SUITE DE TESTES VMS - EXECUÇÃO COMPLETA
echo ========================================

echo Verificando dependências...
python -c "import aiohttp, psutil" 2>nul
if errorlevel 1 (
    echo Instalando dependências...
    pip install aiohttp psutil
)

echo.
echo ========================================
echo 1. TESTE DE STREAMING E LATÊNCIA
echo ========================================
python tests/test_streaming_capacity.py

echo.
echo ========================================
echo 2. TESTE DE DETECÇÕES DE IA
echo ========================================
python tests/test_detections.py

echo.
echo ========================================
echo 3. TESTE DE CAPACIDADE MÁXIMA
echo ========================================
python tests/test_system_capacity.py

echo.
echo ========================================
echo TESTES CONCLUÍDOS!
echo ========================================
echo Verifique os resultados acima para:
echo - Latência e qualidade de streaming
echo - Status das detecções de IA
echo - Capacidade máxima do sistema
echo ========================================

pause