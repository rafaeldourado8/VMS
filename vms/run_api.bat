@echo off
echo ========================================
echo VMS API - FastAPI Server
echo ========================================
echo.
echo Iniciando servidor em http://localhost:8000
echo Documentacao: http://localhost:8000/docs
echo.

cd src
..\venv\Scripts\uvicorn main:app --reload --host 0.0.0.0 --port 8000
