@echo off
echo ========================================
echo  Analise de Complexidade Ciclomatica
echo ========================================
echo.

cd backend

echo [1/4] Domain Layer:
echo -------------------
radon cc domain/ -a -s

echo.
echo [2/4] Application Layer:
echo ------------------------
radon cc application/ -a -s

echo.
echo [3/4] Infrastructure Layer:
echo ---------------------------
radon cc infrastructure/ -a -s

echo.
echo ========================================
echo  Metodos com CC ^> 10 (CRITICO)
echo ========================================
radon cc domain/ application/ infrastructure/ -n C -s

echo.
echo ========================================
echo  Resumo Geral
echo ========================================
radon cc domain/ application/ infrastructure/ -a --total-average

echo.
pause
