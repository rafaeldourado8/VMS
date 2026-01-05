#!/usr/bin/env python3
import requests
import time
import json

# Teste rápido do HLS
def test_hls():
    print("Testando HLS...")
    
    # 1. Criar câmera de teste
    test_data = {
        "camera_id": 999,
        "rtsp_url": "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4",
        "name": "Teste HLS",
        "on_demand": False
    }
    
    try:
        # Provisionar
        r = requests.post("http://localhost:8001/cameras/provision", json=test_data, timeout=10)
        print(f"Provision: {r.status_code}")
        if r.status_code == 200:
            print(f"Response: {r.json()}")
        
        # Aguardar
        print("Aguardando 5s...")
        time.sleep(5)
        
        # Testar HLS direto
        r = requests.get("http://localhost:8888/cam_999/index.m3u8", timeout=5)
        print(f"HLS direto: {r.status_code}")
        
        # Testar via HAProxy
        r = requests.get("http://localhost/hls/cam_999/index.m3u8", timeout=5)
        print(f"HLS via HAProxy: {r.status_code}")
        
        if r.status_code == 200:
            print("HLS funcionando!")
            print(f"Playlist: {r.text[:200]}...")
        else:
            print("HLS falhou: {}".format(r.text))
        
        # Limpar
        requests.delete("http://localhost:8001/cameras/999")
        
    except Exception as e:
        print("Erro: {}".format(e))

if __name__ == "__main__":
    test_hls()