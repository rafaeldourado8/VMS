@echo off
echo ========================================
echo DELETAR BRANCHES ANTIGAS
echo ========================================
echo.
echo ATENCAO: Isso vai deletar branches locais e remotas!
echo.
set /p confirm="Tem certeza? (S/N): "
if /i "%confirm%"=="S" goto continue
if /i "%confirm%"=="Y" goto continue
if /i "%confirm%"=="1" goto continue
if /i "%confirm%"=="SIM" goto continue
if /i "%confirm%"=="YES" goto continue
echo Cancelado.
pause
exit /b

:continue
echo.

echo Deletando branches LOCAIS...
git branch -D alpr 2>nul
git branch -D descart 2>nul
git branch -D dvr-lite 2>nul
git branch -D frontend 2>nul
git branch -D ia-detection 2>nul
git branch -D main 2>nul
git branch -D mvp 2>nul
git branch -D recording 2>nul
git branch -D sprint-2-multi-tenant 2>nul
git branch -D versao-1 2>nul
git branch -D vms-v1-mvp 2>nul
git branch -D vms-v3 2>nul
echo.

echo Deletando branches REMOTAS...
git push origin --delete alpr 2>nul
git push origin --delete dvr-lite 2>nul
git push origin --delete frontend 2>nul
git push origin --delete ia-detection 2>nul
git push origin --delete main 2>nul
git push origin --delete mvp 2>nul
git push origin --delete mvp-1 2>nul
git push origin --delete recording 2>nul
git push origin --delete sprint-2-multi-tenant 2>nul
git push origin --delete versao-1 2>nul
git push origin --delete vms-v1-mvp 2>nul
git push origin --delete vms-v3 2>nul
echo.

echo Atualizando HEAD remoto...
git remote set-head origin dev
echo.

echo ========================================
echo CONCLUIDO!
echo ========================================
echo.
echo Branches restantes:
git branch -a
echo.
pause
