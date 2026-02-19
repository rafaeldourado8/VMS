@echo off
echo ========================================
echo REORGANIZACAO SIMPLES DE BRANCHES
echo ========================================
echo.
echo Pressione ENTER para continuar ou CTRL+C para cancelar
pause >nul
echo.

REM Passo 1: Commit
echo [1/5] Commitando mudancas...
git add .
git commit -m "chore: reorganizacao de branches"
echo.

REM Passo 2: Renomear
echo [2/5] Renomeando para 'local'...
git branch -m local
echo.

REM Passo 3: Criar dev e prod
echo [3/5] Criando dev e prod...
git branch dev
git branch prod
echo.

REM Passo 4: Push
echo [4/5] Fazendo push...
git push -u origin local
git push origin dev
git push origin prod
echo.

REM Passo 5: Mostrar resultado
echo [5/5] Branches atuais:
git branch
echo.

echo ========================================
echo CONCLUIDO!
echo ========================================
echo.
echo Para deletar branches antigas, execute:
echo   delete_old_branches.bat
echo.
pause
