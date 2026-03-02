@echo off
REM Setup AWS Infrastructure - VMS Dev Environment
REM Run as Administrator

echo ========================================
echo VMS - AWS Dev Setup
echo ========================================
echo.

REM Check AWS CLI
echo [1/8] Checking AWS CLI...
aws --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: AWS CLI not found. Installing...
    winget install Amazon.AWSCLI
    echo Please restart terminal and run again
    pause
    exit /b 1
)
echo OK - AWS CLI found

REM Check Terraform
echo [2/8] Checking Terraform...
terraform --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Terraform not found. Installing...
    winget install Hashicorp.Terraform
    echo Please restart terminal and run again
    pause
    exit /b 1
)
echo OK - Terraform found

REM Check AWS credentials
echo [3/8] Checking AWS credentials...
aws sts get-caller-identity >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: AWS credentials not configured
    echo Run: aws configure
    pause
    exit /b 1
)
echo OK - AWS credentials configured

REM Create S3 bucket for Terraform state
echo [4/8] Creating S3 bucket for Terraform state...
aws s3 mb s3://vms-terraform-state --region us-east-1 2>nul
if %errorlevel% equ 0 (
    echo OK - S3 bucket created
) else (
    echo WARNING - Bucket may already exist
)

REM Create ECR repositories
echo [5/8] Creating ECR repositories...
for %%s in (backend frontend lpr recording onvif) do (
    echo Creating vms/%%s...
    aws ecr create-repository --repository-name vms/%%s --region us-east-1 2>nul
)
echo OK - ECR repositories created

REM Get ECR registry URL
echo [6/8] Getting ECR registry URL...
for /f "tokens=*" %%i in ('aws sts get-caller-identity --query Account --output text') do set ACCOUNT_ID=%%i
set ECR_REGISTRY=%ACCOUNT_ID%.dkr.ecr.us-east-1.amazonaws.com
echo ECR Registry: %ECR_REGISTRY%
echo.
echo IMPORTANT: Add this to GitHub Secrets:
echo   ECR_REGISTRY = %ECR_REGISTRY%
echo.

REM Initialize Terraform
echo [7/8] Initializing Terraform...
cd terraform\dev
terraform init
if %errorlevel% neq 0 (
    echo ERROR: Terraform init failed
    pause
    exit /b 1
)
echo OK - Terraform initialized

REM Plan Terraform
echo [8/8] Planning Terraform deployment...
terraform plan -out=tfplan
if %errorlevel% neq 0 (
    echo ERROR: Terraform plan failed
    pause
    exit /b 1
)
echo OK - Terraform plan created

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Review the Terraform plan above
echo 2. Add GitHub Secrets (see docs/QUICK_START_AWS.md)
echo 3. Run: terraform apply tfplan
echo 4. Wait ~10 minutes for resources to be created
echo 5. Run: terraform output
echo.
echo Estimated cost: ~$43/month
echo.
pause
