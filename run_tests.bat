@echo off
REM Script para executar testes via Docker Compose (Windows)

echo 🧪 GT-Vision Backend Test Suite (Docker)
echo =========================================
echo.

REM Verificar se containers estão rodando
docker-compose ps | findstr "Up" >nul
if errorlevel 1 (
    echo Iniciando containers...
    docker-compose up -d postgres_db redis_cache
    timeout /t 5 /nobreak >nul
)

REM Menu de opções
if "%1"=="" goto all
if "%1"=="all" goto all
if "%1"=="crud" goto crud
if "%1"=="security" goto security
if "%1"=="performance" goto performance
if "%1"=="persistence" goto persistence
if "%1"=="streaming" goto streaming
if "%1"=="load" goto load
if "%1"=="coverage" goto coverage
if "%1"=="quick" goto quick
if "%1"=="critical" goto critical
goto usage

:all
echo Running ALL tests...
echo.
docker-compose exec -T backend pytest testes/ -v
goto end

:crud
echo Running CRUD tests...
docker-compose exec -T backend pytest testes/crud/ -v
goto end

:security
echo Running Security tests...
docker-compose exec -T backend pytest testes/seguranca/ -v
goto end

:performance
echo Running Performance tests...
docker-compose exec -T backend pytest testes/velocidade/ -v
goto end

:persistence
echo Running Persistence tests...
docker-compose exec -T backend pytest testes/persistencia/ -v
goto end

:streaming
echo Running Streaming tests...
docker-compose exec -T backend pytest testes/streaming/ -v
goto end

:load
echo Running Load tests...
docker-compose exec -T backend pytest testes/carga/ -v
goto end

:coverage
echo Running tests with coverage...
docker-compose exec -T backend pytest testes/ --cov=apps --cov-report=html --cov-report=term
echo.
echo Coverage report generated in backend/htmlcov/index.html
goto end

:quick
echo Running quick tests (excluding load tests)...
docker-compose exec -T backend pytest testes/ -v --ignore=testes/carga/
goto end

:critical
echo Running critical tests only...
docker-compose exec -T backend pytest testes/seguranca/ testes/crud/test_cameras_crud.py::TestCamerasCRUD::test_create_camera -v
goto end

:usage
echo Usage: run_tests.bat [option]
echo.
echo Options:
echo   all          - Run all tests (default)
echo   crud         - Run CRUD tests
echo   security     - Run security tests
echo   performance  - Run performance tests
echo   persistence  - Run persistence tests
echo   streaming    - Run streaming tests
echo   load         - Run load tests
echo   coverage     - Run with coverage report
echo   quick        - Run quick tests (no load)
echo   critical     - Run critical tests only
exit /b 1

:end
echo.
echo ✅ Tests completed!
