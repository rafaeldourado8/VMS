# Execute como Administrador
Write-Host "Liberando portas do MediaMTX no Firewall do Windows..." -ForegroundColor Yellow

# RTSP
New-NetFirewallRule -DisplayName "MediaMTX RTSP" -Direction Inbound -Protocol TCP -LocalPort 8554 -Action Allow -ErrorAction SilentlyContinue
Write-Host "[OK] Porta 8554 (RTSP) liberada" -ForegroundColor Green

# API
New-NetFirewallRule -DisplayName "MediaMTX API" -Direction Inbound -Protocol TCP -LocalPort 9997 -Action Allow -ErrorAction SilentlyContinue
Write-Host "[OK] Porta 9997 (API) liberada" -ForegroundColor Green

# HLS
New-NetFirewallRule -DisplayName "MediaMTX HLS" -Direction Inbound -Protocol TCP -LocalPort 8888 -Action Allow -ErrorAction SilentlyContinue
Write-Host "[OK] Porta 8888 (HLS) liberada" -ForegroundColor Green

Write-Host "`nFirewall configurado com sucesso!" -ForegroundColor Green
Write-Host "Seu IP: 192.168.0.103" -ForegroundColor Cyan
Write-Host "URL RTSP: rtsp://192.168.0.103:8554/NOME_DA_CAMERA" -ForegroundColor Cyan

pause
