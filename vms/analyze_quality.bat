@echo off
echo ========================================
echo VMS - Analise Completa de Qualidade
echo ========================================
echo.
echo Este script ira executar:
echo 1. Testes com Coverage
echo 2. Complexidade Ciclomatica (Radon)
echo 3. Analise SOLID (Pylint)
echo 4. Analise de Seguranca (Bandit)
echo 5. Dead Code Detection (Vulture)
echo.
pause

REM ========================================
REM 1. TESTES COM COVERAGE
REM ========================================
echo.
echo ========================================
echo [1/5] TESTES COM COVERAGE
echo ========================================
echo.

echo Testando Admin...
cd src\admin
..\..\venv\Scripts\pytest tests\unit -v --cov=. --cov-report=html:../../reports/coverage/admin
cd ..\..

echo.
echo Testando Cidades...
cd src\cidades
..\..\venv\Scripts\pytest tests\unit -v --cov=. --cov-report=html:../../reports/coverage/cidades
cd ..\..

echo.
echo Testando Cameras...
cd src\cameras
..\..\venv\Scripts\pytest tests\unit -v --cov=. --cov-report=html:../../reports/coverage/cameras
cd ..\..

echo.
echo Testando Streaming...
cd src\streaming
..\..\venv\Scripts\pytest tests\unit -v --cov=. --cov-report=html:../../reports/coverage/streaming
cd ..\..

echo.
echo Testando LPR...
cd src\lpr
..\..\venv\Scripts\pytest tests\unit -v --cov=. --cov-report=html:../../reports/coverage/lpr
cd ..\..

REM ========================================
REM 2. COMPLEXIDADE CICLOMATICA
REM ========================================
echo.
echo ========================================
echo [2/5] COMPLEXIDADE CICLOMATICA
echo ========================================
echo.

venv\Scripts\radon cc src -a -s > reports\complexity.txt
type reports\complexity.txt

REM ========================================
REM 3. ANALISE SOLID (PYLINT)
REM ========================================
echo.
echo ========================================
echo [3/5] ANALISE SOLID (PYLINT)
echo ========================================
echo.

venv\Scripts\pylint src\admin --disable=C0114,C0115,C0116 --max-line-length=120 > reports\pylint_admin.txt 2>&1
venv\Scripts\pylint src\cidades --disable=C0114,C0115,C0116 --max-line-length=120 > reports\pylint_cidades.txt 2>&1
venv\Scripts\pylint src\cameras --disable=C0114,C0115,C0116 --max-line-length=120 > reports\pylint_cameras.txt 2>&1
venv\Scripts\pylint src\streaming --disable=C0114,C0115,C0116 --max-line-length=120 > reports\pylint_streaming.txt 2>&1
venv\Scripts\pylint src\lpr --disable=C0114,C0115,C0116 --max-line-length=120 > reports\pylint_lpr.txt 2>&1

echo Relatorios salvos em reports\pylint_*.txt

REM ========================================
REM 4. ANALISE DE SEGURANCA (BANDIT)
REM ========================================
echo.
echo ========================================
echo [4/5] ANALISE DE SEGURANCA (BANDIT)
echo ========================================
echo.

venv\Scripts\bandit -r src -f txt -o reports\security.txt
type reports\security.txt

REM ========================================
REM 5. DEAD CODE DETECTION (VULTURE)
REM ========================================
echo.
echo ========================================
echo [5/5] DEAD CODE DETECTION (VULTURE)
echo ========================================
echo.

venv\Scripts\vulture src --min-confidence 80 > reports\deadcode.txt
type reports\deadcode.txt

REM ========================================
REM RESUMO
REM ========================================
echo.
echo ========================================
echo ANALISE COMPLETA!
echo ========================================
echo.
echo Relatorios gerados em:
echo - reports\coverage\*\index.html (Coverage HTML)
echo - reports\complexity.txt (Complexidade)
echo - reports\pylint_*.txt (SOLID)
echo - reports\security.txt (Seguranca)
echo - reports\deadcode.txt (Dead Code)
echo.
pause
