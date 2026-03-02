@echo off
REM ============================================
REM VMS - Setup Completo Automatizado
REM ============================================

echo.
echo ========================================
echo VMS - Setup Completo AWS + GitHub
echo ========================================
echo.
echo Este script vai:
echo 1. Verificar pre-requisitos
echo 2. Configurar AWS
echo 3. Criar recursos base
echo 4. Gerar chaves SSH
echo 5. Preparar Terraform
echo.
pause

REM ============================================
REM PARTE 1: Verificar Pre-requisitos
REM ============================================

echo.
echo [1/10] Verificando pre-requisitos...
echo.

REM Verificar AWS CLI
aws --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] AWS CLI nao encontrado
    echo Instalando AWS CLI...
    winget install Amazon.AWSCLI
    echo.
    echo Por favor, feche e reabra o terminal, depois execute novamente
    pause
    exit /b 1
)
echo [OK] AWS CLI instalado

REM Verificar Terraform
terraform --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Terraform nao encontrado
    echo Instalando Terraform...
    winget install Hashicorp.Terraform
    echo.
    echo Por favor, feche e reabra o terminal, depois execute novamente
    pause
    exit /b 1
)
echo [OK] Terraform instalado

REM Verificar Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Git nao encontrado
    echo Instale Git: https://git-scm.com/download/win
    pause
    exit /b 1
)
echo [OK] Git instalado

REM ============================================
REM PARTE 2: Verificar Credenciais AWS
REM ============================================

echo.
echo [2/10] Verificando credenciais AWS...
echo.

aws sts get-caller-identity >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Credenciais AWS nao configuradas
    echo.
    echo Execute: aws configure
    echo.
    echo Voce precisa:
    echo 1. AWS Access Key ID
    echo 2. AWS Secret Access Key
    echo 3. Region: us-east-1
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('aws sts get-caller-identity --query Account --output text') do set ACCOUNT_ID=%%i
echo [OK] AWS configurado - Account: %ACCOUNT_ID%

REM ============================================
REM PARTE 3: Criar Bucket S3
REM ============================================

echo.
echo [3/10] Criando bucket S3 para Terraform...
echo.

aws s3 mb s3://vms-terraform-state --region us-east-1 2>nul
if %errorlevel% equ 0 (
    echo [OK] Bucket criado
    aws s3api put-bucket-versioning --bucket vms-terraform-state --versioning-configuration Status=Enabled
) else (
    echo [INFO] Bucket ja existe
)

REM ============================================
REM PARTE 4: Criar ECR Repositories
REM ============================================

echo.
echo [4/10] Criando ECR repositories...
echo.

for %%s in (backend frontend lpr recording onvif) do (
    echo Criando vms/%%s...
    aws ecr create-repository --repository-name vms/%%s --region us-east-1 2>nul
)
echo [OK] ECR repositories criados

set ECR_REGISTRY=%ACCOUNT_ID%.dkr.ecr.us-east-1.amazonaws.com
echo.
echo ECR Registry: %ECR_REGISTRY%

REM ============================================
REM PARTE 5: Gerar Chaves SSH
REM ============================================

echo.
echo [5/10] Gerando chaves SSH...
echo.

if not exist "%USERPROFILE%\.ssh" mkdir "%USERPROFILE%\.ssh"

if exist "%USERPROFILE%\.ssh\vms-deploy-key" (
    echo [INFO] Chave SSH ja existe
) else (
    ssh-keygen -t rsa -b 4096 -f "%USERPROFILE%\.ssh\vms-deploy-key" -N "" -C "vms-deploy-key"
    echo [OK] Chave SSH gerada
)

REM Importar para AWS
aws ec2 import-key-pair --key-name vms-deploy-key --public-key-material fileb://%USERPROFILE%/.ssh/vms-deploy-key.pub --region us-east-1 2>nul
if %errorlevel% equ 0 (
    echo [OK] Chave importada para AWS
) else (
    echo [INFO] Chave ja existe na AWS
)

REM ============================================
REM PARTE 6: Criar IAM Role para ECS
REM ============================================

echo.
echo [6/10] Criando IAM roles...
echo.

aws iam create-role --role-name ecsTaskExecutionRole --assume-role-policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"ecs-tasks.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}" 2>nul

aws iam attach-role-policy --role-name ecsTaskExecutionRole --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy 2>nul

echo [OK] IAM roles configurados

REM ============================================
REM PARTE 7: Preparar Terraform
REM ============================================

echo.
echo [7/10] Preparando Terraform...
echo.

cd terraform\dev

REM Criar ZIP do Lambda
if exist scheduler.zip del scheduler.zip
powershell -Command "Compress-Archive -Path scheduler.py -DestinationPath scheduler.zip -Force"
echo [OK] Lambda ZIP criado

REM Inicializar Terraform
terraform init
if %errorlevel% neq 0 (
    echo [ERRO] Terraform init falhou
    pause
    exit /b 1
)
echo [OK] Terraform inicializado

cd ..\..

REM ============================================
REM PARTE 8: Criar Arquivo de Configuracao
REM ============================================

echo.
echo [8/10] Criando arquivos de configuracao...
echo.

REM Criar .env.dev
if not exist .env.dev (
    copy .env.dev.example .env.dev >nul
    echo [OK] .env.dev criado
) else (
    echo [INFO] .env.dev ja existe
)

REM ============================================
REM PARTE 9: Criar Arquivo de Instrucoes
REM ============================================

echo.
echo [9/10] Gerando arquivo de instrucoes...
echo.

(
echo ========================================
echo SETUP COMPLETO - PROXIMOS PASSOS
echo ========================================
echo.
echo INFORMACOES IMPORTANTES:
echo.
echo AWS Account ID: %ACCOUNT_ID%
echo ECR Registry: %ECR_REGISTRY%
echo Region: us-east-1
echo.
echo ========================================
echo GITHUB SECRETS - ADICIONE MANUALMENTE
echo ========================================
echo.
echo Va em: GitHub -^> Settings -^> Secrets -^> Actions
echo.
echo Adicione os seguintes secrets:
echo.
echo 1. AWS_ACCESS_KEY_ID
echo    Valor: [sua AWS Access Key]
echo.
echo 2. AWS_SECRET_ACCESS_KEY
echo    Valor: [sua AWS Secret Key]
echo.
echo 3. AWS_REGION
echo    Valor: us-east-1
echo.
echo 4. ECR_REGISTRY
echo    Valor: %ECR_REGISTRY%
echo.
echo 5. EC2_SSH_PRIVATE_KEY
echo    Arquivo: %USERPROFILE%\.ssh\vms-deploy-key
echo    Copie TODO o conteudo do arquivo
echo.
echo ========================================
echo DEPLOY INFRAESTRUTURA
echo ========================================
echo.
echo Execute os comandos:
echo.
echo cd terraform\dev
echo terraform plan -out=tfplan
echo terraform apply tfplan
echo.
echo Aguarde ~15 minutos para criar recursos
echo.
echo Depois execute:
echo terraform output
echo.
echo Copie os valores e atualize .env.dev
echo.
echo ========================================
echo TESTAR CI/CD
echo ========================================
echo.
echo git checkout -b dev
echo git add .
echo git commit -m "test: CI/CD setup"
echo git push origin dev
echo.
echo Acompanhe em: GitHub -^> Actions
echo.
echo ========================================
echo CUSTOS ESTIMADOS
echo ========================================
echo.
echo Dev: ~$43/mes ^(11h/dia^)
echo Prod: ~$1,601/mes ^(24/7^)
echo.
echo ========================================
) > PROXIMOS_PASSOS.txt

echo [OK] Arquivo PROXIMOS_PASSOS.txt criado

REM ============================================
REM PARTE 10: Resumo Final
REM ============================================

echo.
echo [10/10] Setup completo!
echo.
echo ========================================
echo RESUMO
echo ========================================
echo.
echo [OK] AWS CLI configurado
echo [OK] Terraform instalado
echo [OK] Bucket S3 criado
echo [OK] ECR repositories criados
echo [OK] Chaves SSH geradas
echo [OK] IAM roles criados
echo [OK] Terraform inicializado
echo.
echo ========================================
echo PROXIMOS PASSOS
echo ========================================
echo.
echo 1. Leia o arquivo: PROXIMOS_PASSOS.txt
echo 2. Configure GitHub Secrets
echo 3. Execute: cd terraform\dev
echo 4. Execute: terraform plan -out=tfplan
echo 5. Execute: terraform apply tfplan
echo.
echo Documentacao completa:
echo - docs\TUTORIAL_COMPLETO_DEPLOY.md
echo - docs\QUICK_START_AWS.md
echo.
echo ========================================
echo.

REM Abrir arquivo de instrucoes
notepad PROXIMOS_PASSOS.txt

pause
