# Script de Teste da API - GTVision
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testando API GTVision" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Testar Health Check
Write-Host "[1/6] Testando Health Check..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health/" -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ Health Check OK - Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host $response.Content
} catch {
    Write-Host "❌ Health Check FALHOU: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 2. Testar Admin Login Page
Write-Host "[2/6] Testando Admin Login..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/admin/login/" -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ Admin Login OK - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Admin Login FALHOU: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 3. Testar API Root (deve retornar erro de autenticação)
Write-Host "[3/6] Testando API Root (espera-se erro de autenticação)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/" -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ API Root OK - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    if ($_.Exception.Response.StatusCode -eq 401 -or $_.Exception.Response.StatusCode -eq 403) {
        Write-Host "✅ API protegida corretamente (401/403)" -ForegroundColor Green
    } else {
        Write-Host "❌ Erro inesperado: $($_.Exception.Message)" -ForegroundColor Red
    }
}
Write-Host ""

# 4. Testar Kong Gateway
Write-Host "[4/6] Testando Kong Gateway..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/" -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ Kong OK - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Kong FALHOU: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 5. Testar HAProxy Stats
Write-Host "[5/6] Testando HAProxy Stats..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8404/stats" -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ HAProxy OK - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ HAProxy FALHOU: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 6. Testar Frontend
Write-Host "[6/6] Testando Frontend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173/" -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ Frontend OK - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend FALHOU: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Resumo
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "URLs de Acesso:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Frontend:        http://localhost:5173" -ForegroundColor White
Write-Host "API (Kong):      http://localhost:8000/api/" -ForegroundColor White
Write-Host "Admin Django:    http://localhost:8000/admin/" -ForegroundColor White
Write-Host "HAProxy Stats:   http://localhost:8404/stats" -ForegroundColor White
Write-Host "Kong Admin:      http://localhost:8001/" -ForegroundColor White
Write-Host "RabbitMQ:        http://localhost:15672/" -ForegroundColor White
Write-Host "MediaMTX API:    http://localhost:9997/" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar logs do Celery
Write-Host "Logs do Celery Worker (últimas 10 linhas):" -ForegroundColor Yellow
docker-compose logs --tail=10 backend_worker
