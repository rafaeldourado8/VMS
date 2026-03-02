@echo off
setlocal enabledelayedexpansion

cd /d %~dp0..\..\terraform\dev

echo Obtendo Instance ID...
for /f "delims=" %%i in ('terraform output -raw instance_id 2^>nul') do set INSTANCE_ID=%%i

if "%INSTANCE_ID%"=="" (
    echo ERRO: Instance ID nao encontrado. Execute terraform apply primeiro.
    pause
    exit /b 1
)

echo Iniciando instancia: %INSTANCE_ID%
aws ec2 start-instances --instance-ids %INSTANCE_ID%

echo Aguardando instancia iniciar...
aws ec2 wait instance-running --instance-ids %INSTANCE_ID%

for /f "delims=" %%i in ('terraform output -raw public_ip') do set PUBLIC_IP=%%i

echo.
echo ========================================
echo Instancia iniciada!
echo ========================================
echo Public IP: %PUBLIC_IP%
echo SSH: ssh -i vms-dev-key.pem ubuntu@%PUBLIC_IP%
echo.
pause
