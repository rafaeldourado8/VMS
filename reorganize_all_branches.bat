@echo off
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
if /i not "%confirm%"=="S" (
    echo Operacao cancelada.
    pause
    exit /b
)
echo.

REM ===== PARTE 1: LOCAL =====
echo [PARTE 1] Reorganizando branches LOCAIS...
echo.

echo [1/8] Commitando mudancas atuais...
git add .
git commit -m "chore: consolidacao antes da reorganizacao de branches"
echo.

echo [2/8] Renomeando branch atual para 'local'...
git branch -m vms-v3 local
echo.

echo [3/8] Criando branch 'dev'...
git branch dev
echo.

echo [4/8] Criando branch 'prod'...
git branch prod
echo.

echo [5/8] Deletando branches locais antigas...
for %%b in (alpr descart dvr-lite frontend ia-detection main mvp recording sprint-2-multi-tenant versao-1 vms-v1-mvp) do (
    git branch -D %%b 2>nul
)
echo.

REM ===== PARTE 2: REMOTO =====
echo [PARTE 2] Atualizando branches REMOTAS...
echo.

echo [6/8] Fazendo push das novas branches...
git push -u origin local
git push -u origin dev
git push -u origin prod
echo.

echo [7/8] Deletando branches remotas antigas...
for %%b in (alpr dvr-lite frontend ia-detection main mvp mvp-1 recording sprint-2-multi-tenant versao-1 vms-v1-mvp vms-v3) do (
    git push origin --delete %%b 2>nul
)
echo.

echo [8/8] Atualizando HEAD remoto...
git remote set-head origin dev
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
