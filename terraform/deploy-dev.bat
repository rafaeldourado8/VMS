@echo off
echo ========================================
echo VMS - Deploy Desenvolvimento (Terraform)
echo ========================================
echo.

cd /d %~dp0dev

echo [1/5] Verificando Terraform...
terraform version
if errorlevel 1 (
    echo ERRO: Terraform nao encontrado. Instale: https://www.terraform.io/downloads
    pause
    exit /b 1
)

echo.
echo [2/5] Verificando AWS CLI...
aws sts get-caller-identity
if errorlevel 1 (
    echo ERRO: AWS CLI nao configurado. Execute: aws configure
    pause
    exit /b 1
)

echo.
echo [3/5] Inicializando Terraform...
terraform init

echo.
echo [4/5] Validando configuracao...
terraform validate

echo.
echo [5/5] Planejando deploy...
terraform plan

echo.
echo ========================================
echo Pronto para aplicar!
echo Execute: terraform apply
echo ========================================
pause
