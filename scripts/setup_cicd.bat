@echo off
echo ========================================
echo VMS - Setup Completo CI/CD
echo ========================================
echo.

echo [1/6] Verificando pre-requisitos...
echo.

terraform version >nul 2>&1
if errorlevel 1 (
    echo [X] Terraform nao encontrado
    echo Instale: https://www.terraform.io/downloads
    pause
    exit /b 1
)
echo [OK] Terraform instalado

where aws >nul 2>&1
if errorlevel 1 (
    set "PATH=%PATH%;C:\Program Files\Amazon\AWSCLIV2"
    where aws >nul 2>&1
    if errorlevel 1 (
        echo [X] AWS CLI nao encontrado
        echo Instale: https://aws.amazon.com/cli/
        pause
        exit /b 1
    )
)
echo [OK] AWS CLI instalado

aws sts get-caller-identity >nul 2>&1
if errorlevel 1 (
    echo [X] AWS CLI nao configurado
    echo Execute: aws configure
    pause
    exit /b 1
)
echo [OK] AWS CLI configurado

echo.
echo [2/6] Criando SSH Key Pair...
aws ec2 describe-key-pairs --key-names vms-dev-key >nul 2>&1
if errorlevel 1 (
    echo Criando key pair...
    aws ec2 create-key-pair --key-name vms-dev-key --query "KeyMaterial" --output text > vms-dev-key.pem
    echo [OK] Key pair criado: vms-dev-key.pem
) else (
    echo [OK] Key pair ja existe
)

echo.
echo [3/6] Configurando Terraform...
cd terraform\dev

if not exist terraform.tfvars (
    copy terraform.tfvars.example terraform.tfvars
    echo [!] Edite terraform\dev\terraform.tfvars com seu IP
    notepad terraform.tfvars
)

echo.
echo [4/6] Inicializando Terraform...
terraform init

echo.
echo [5/6] Validando configuracao...
terraform validate

echo.
echo [6/6] Pronto para deploy!
echo.
echo ========================================
echo Proximos passos:
echo ========================================
echo 1. terraform apply (criar EC2)
echo 2. ssh -i vms-dev-key.pem ubuntu@^<IP^>
echo 3. git clone https://github.com/SEU_USUARIO/VMS.git
echo 4. bash scripts/setup_runner.sh ^<TOKEN^>
echo 5. Configurar secrets no GitHub
echo 6. git push origin develop (testar CI/CD)
echo.
echo Documentacao: docs\CI_CD_SETUP.md
echo ========================================
pause
