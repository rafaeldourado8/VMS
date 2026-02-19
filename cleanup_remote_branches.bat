@echo off
echo ========================================
echo Limpando Branches REMOTAS
echo ========================================
echo.
echo ATENCAO: Este script vai DELETAR branches remotas!
echo.
echo Branches que serao MANTIDAS:
echo   - dev
echo   - prod
echo.
echo Branches que serao DELETADAS:
echo   - alpr
echo   - dvr-lite
echo   - frontend
echo   - ia-detection
echo   - main
echo   - mvp
echo   - mvp-1
echo   - recording
echo   - sprint-2-multi-tenant
echo   - versao-1
echo   - vms-v1-mvp
echo   - vms-v3
echo.
set /p confirm="Tem certeza? (S/N): "
if /i not "%confirm%"=="S" (
    echo Operacao cancelada.
    pause
    exit /b
)
echo.

echo Deletando branches remotas...
for %%b in (alpr dvr-lite frontend ia-detection main mvp mvp-1 recording sprint-2-multi-tenant versao-1 vms-v1-mvp vms-v3) do (
    echo Deletando origin/%%b...
    git push origin --delete %%b
)
echo.

echo Atualizando HEAD remoto para dev...
git push origin dev
git remote set-head origin dev
echo.

echo ========================================
echo Limpeza REMOTA concluida!
echo ========================================
echo.
echo Branches remotas restantes:
git branch -r
echo.
pause
