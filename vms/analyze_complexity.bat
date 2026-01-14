@echo off
echo ========================================
echo Analise de Complexidade Ciclomatica
echo ========================================
echo.

echo [1/5] Analisando modulo Admin...
venv\Scripts\radon cc src\admin -a -s

echo.
echo [2/5] Analisando modulo Cidades...
venv\Scripts\radon cc src\cidades -a -s

echo.
echo [3/5] Analisando modulo Cameras...
venv\Scripts\radon cc src\cameras -a -s

echo.
echo [4/5] Analisando modulo Streaming...
venv\Scripts\radon cc src\streaming -a -s

echo.
echo [5/5] Analisando modulo LPR...
venv\Scripts\radon cc src\lpr -a -s

echo.
echo ========================================
echo Analise Completa!
echo ========================================
pause
