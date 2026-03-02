@echo off
setlocal enabledelayedexpansion

cd /d %~dp0..\..\terraform\dev

echo Obtendo Instance ID...
for /f "delims=" %%i in ('terraform output -raw instance_id 2^>nul') do set INSTANCE_ID=%%i

if "%INSTANCE_ID%"=="" (
    echo ERRO: Instance ID nao encontrado.
    pause
    exit /b 1
)

echo Parando instancia: %INSTANCE_ID%
aws ec2 stop-instances --instance-ids %INSTANCE_ID%

echo Aguardando instancia parar...
aws ec2 wait instance-stopped --instance-ids %INSTANCE_ID%

echo.
echo ========================================
echo Instancia parada!
echo ========================================
echo Voce esta economizando ~$0.03/hora
echo.
echo Para iniciar novamente: start-dev.bat
echo.
pause
