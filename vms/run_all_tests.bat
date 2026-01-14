@echo off
echo ========================================
echo Executando Testes com Coverage
echo ========================================
echo.

echo [1/5] Testando modulo Admin...
cd src\admin
..\..\venv\Scripts\pytest tests\unit -v --cov=. --cov-report=term-missing
cd ..\..

echo.
echo [2/5] Testando modulo Cidades...
cd src\cidades
..\..\venv\Scripts\pytest tests\unit -v --cov=. --cov-report=term-missing
cd ..\..

echo.
echo [3/5] Testando modulo Cameras...
cd src\cameras
..\..\venv\Scripts\pytest tests\unit -v --cov=. --cov-report=term-missing
cd ..\..

echo.
echo [4/5] Testando modulo Streaming...
cd src\streaming
..\..\venv\Scripts\pytest tests\unit -v --cov=. --cov-report=term-missing
cd ..\..

echo.
echo [5/5] Testando modulo LPR...
cd src\lpr
..\..\venv\Scripts\pytest tests\unit -v --cov=. --cov-report=term-missing
cd ..\..

echo.
echo ========================================
echo Testes Completos!
echo ========================================
pause
