#!/usr/bin/env python3
"""Provisiona todas as câmeras LPR em lote."""

import json
import requests
import time

API_URL = "http://localhost:8001/cameras/provision"

with open("cameras_lpr.json") as f:
    data = json.load(f)

total = 0
success = 0
failed = []

for city, cameras in data.items():
    print(f"\n{'='*60}")
    print(f"{city.upper()}")
    print(f"{'='*60}")
    
    for cam in cameras:
        total += 1
        print(f"\n[{total}] Provisionando cam_{cam['camera_id']}: {cam['name']}")
        
        try:
            resp = requests.post(API_URL, json=cam, timeout=30)
            result = resp.json()
            
            if result.get("success"):
                print(f"    OK - {result['hls_url']}")
                success += 1
            else:
                print(f"    FALHOU - {result.get('message', 'Erro desconhecido')}")
                failed.append(cam['camera_id'])
        except Exception as e:
            print(f"    ERRO - {e}")
            failed.append(cam['camera_id'])
        
        time.sleep(2)

print(f"\n{'='*60}")
print(f"RESUMO")
print(f"{'='*60}")
print(f"Total: {total}")
print(f"Sucesso: {success}")
print(f"Falhas: {len(failed)}")
if failed:
    print(f"IDs com falha: {failed}")
