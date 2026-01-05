#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar provisionamento de cameras reais no VMS
"""
import requests
import time
import sys

BACKEND_URL = "http://localhost/api"

CAMERAS = [
    {"name": "Camera Intelbras 1", "rtsp_url": "rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1&subtype=0"},
    {"name": "Camera Intelbras 2", "rtsp_url": "rtsp://admin:Camerite123@45.236.226.75:6052/cam/realmonitor?channel=1&subtype=0"},
    {"name": "Camera Intelbras 3", "rtsp_url": "rtsp://admin:Camerite123@45.236.226.74:6050/cam/realmonitor?channel=1&subtype=0"},
    {"name": "Camera RTMP 1", "rtsp_url": "rtmp://inst-iwvio-srs-rtmp-intelbras.camerite.services:1935/record/7KOM27157189T.stream"},
    {"name": "Camera Hikvision 1", "rtsp_url": "rtsp://admin:Camerite@186.226.193.111:602/h264/ch1/main/av_stream"},
]

def create_camera(name, rtsp_url):
    try:
        payload = {
            "name": name,
            "rtsp_url": rtsp_url,
            "location": "Teste Real",
            "is_active": True
        }
        
        response = requests.post(f"{BACKEND_URL}/cameras/", json=payload, timeout=10)
        
        if response.status_code == 201:
            data = response.json()
            camera_id = data.get("id")
            print(f"  [OK] Camera criada: ID {camera_id} - {name}")
            return camera_id
        else:
            print(f"  [ERRO] Status {response.status_code}: {response.text[:100]}")
            return None
            
    except Exception as e:
        print(f"  [ERRO] {e}")
        return None

def main():
    print("=" * 70)
    print("TESTE DE PROVISIONAMENTO DE CAMERAS REAIS")
    print("=" * 70)
    print()
    
    print(f"Criando {len(CAMERAS)} cameras...")
    print()
    
    created = []
    
    for i, cam in enumerate(CAMERAS, 1):
        print(f"[{i}/{len(CAMERAS)}] {cam['name']}")
        camera_id = create_camera(cam['name'], cam['rtsp_url'])
        
        if camera_id:
            created.append(camera_id)
        
        time.sleep(1)
    
    print()
    print("=" * 70)
    print(f"RESULTADO: {len(created)}/{len(CAMERAS)} cameras criadas com sucesso")
    print("=" * 70)
    print()
    print("IDs criados:", created)
    print()
    print("Acesse http://localhost para visualizar as cameras")
    print()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTeste interrompido")
        sys.exit(1)
