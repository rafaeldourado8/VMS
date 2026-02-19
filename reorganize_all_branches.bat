@echo off
setlocal enabledelayedexpansion

echo ========================================
echo REORGANIZACAO COMPLETA DE BRANCHES
echo ========================================
echo.
echo Este script vai:
echo   1. Commitar mudancas atuais
echo   2. Renomear vms-v3 para 'local'
echo   3. Criar branches 'dev' e 'prod'
echo   4. Deletar branches locais antigas
echo   5. Fazer push das novas branches
echo   6. Deletar branches remotas antigas
echo.
set /p confirm="Deseja continuar? (S/N): "
if /i "%confirm%"=="S" goto continue
if /i "%confirm%"=="Y" goto continue
if /i "%confirm%"=="1" goto continue
if /i "%confirm%"=="SIM" goto continue
if /i "%confirm%"=="YES" goto continue
echo Operacao cancelada.
pause
exit /b

:continue
echo.

REM ===== PARTE 1: LOCAL =====
echo [PARTE 1] Reorganizando branches LOCAIS...
echo.

echo [1/8] Commitando mudancas atuais...
git add . 2>nul
git commit -m "chore: consolidacao antes da reorganizacao de branches" 2>nul
if errorlevel 1 (
    echo Nenhuma mudanca para commitar ou commit falhou
)
echo.

echo [2/8] Renomeando branch atual para 'local'...
git branch -m local 2>nul
if errorlevel 1 (
    echo Branch ja se chama 'local' ou erro ao renomear
)
echo.

echo [3/8] Criando branch 'dev'...
git branch dev 2>nul
if errorlevel 1 (
    echo Branch 'dev' ja existe
)
echo.

echo [4/8] Criando branch 'prod'...
git branch prod 2>nul
if errorlevel 1 (
    echo Branch 'prod' ja existe
)
echo.

echo [5/8] Deletando branches locais antigas...
for %%b in (alpr descart dvr-lite frontend ia-detection main mvp recording sprint-2-multi-tenant versao-1 vms-v1-mvp vms-v3) do (
    git branch -D %%b >nul 2>&1
    if not errorlevel 1 (
        echo   - Deletada: %%b
    )
)
echo.

REM ===== PARTE 2: REMOTO =====
echo [PARTE 2] Atualizando branches REMOTAS...
echo.

echo [6/8] Fazendo push das novas branches...
echo   - Pushing local...
git push -u origin local 2>nul
echo   - Pushing dev...
git push -u origin dev 2>nul
echo   - Pushing prod...
git push -u origin prod 2>nul
echo.

echo [7/8] Deletando branches remotas antigas...
for %%b in (alpr dvr-lite frontend ia-detection main mvp mvp-1 recording sprint-2-multi-tenant versao-1 vms-v1-mvp vms-v3) do (
    git push origin --delete %%b >nul 2>&1
    if not errorlevel 1 (
        echo   - Deletada remota: %%b
    )
)
echo.

echo [8/8] Atualizando HEAD remoto...
git remote set-head origin dev 2>nul
echo.

REM ===== RESULTADO =====
echo ========================================
echo REORGANIZACAO CONCLUIDA!
echo ========================================
echo.
echo Branches LOCAIS:
git branch
echo.
echo Branches REMOTAS:
git branch -r
echo.
echo ========================================
echo Estrutura final:
echo   - local  : branch de trabalho local
echo   - dev    : branch de desenvolvimento
echo   - prod   : branch de producao
echo ========================================
echo.
pause
