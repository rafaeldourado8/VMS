@echo off
echo ========================================
echo Reorganizando Branches do Repositorio
echo ========================================
echo.

REM Commitar mudancas atuais
echo [1/6] Commitando mudancas atuais...
git add .
git commit -m "chore: consolidacao de mudancas antes da reorganizacao de branches"
echo.

REM Renomear branch atual para 'local'
echo [2/6] Renomeando branch atual para 'local'...
git branch -m vms-v3 local
echo.

REM Criar branch dev a partir de local
echo [3/6] Criando branch 'dev'...
git branch dev
echo.

REM Criar branch prod a partir de local
echo [4/6] Criando branch 'prod'...
git branch prod
echo.

REM Deletar branches locais desnecessarias
echo [5/6] Deletando branches locais antigas...
for %%b in (alpr descart dvr-lite frontend ia-detection main mvp recording sprint-2-multi-tenant versao-1 vms-v1-mvp) do (
    git branch -D %%b 2>nul
    if errorlevel 1 (
        echo   - Branch %%b nao existe localmente
    ) else (
        echo   - Branch %%b deletada
    )
)
echo.

REM Mostrar branches restantes
echo [6/6] Branches atuais:
git branch
echo.

echo ========================================
echo Reorganizacao LOCAL concluida!
echo ========================================
echo.
echo Branches mantidas:
echo   - local (branch atual de trabalho)
echo   - dev (desenvolvimento)
echo   - prod (producao)
echo.
echo IMPORTANTE: Para limpar branches remotas, execute:
echo   git push origin --delete NOME_DA_BRANCH
echo.
echo Ou use o script: cleanup_remote_branches.bat
echo.
pause
