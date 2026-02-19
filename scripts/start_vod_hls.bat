@echo off
echo Iniciando servico VOD HLS na porta 8004...
cd /d d:\VMS
python services\vod_hls_service.py
pause
