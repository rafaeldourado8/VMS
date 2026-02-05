#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime

def check_structure():
    today = datetime.now().strftime("%Y-%m-%d")
    path = Path(f"/recordings/cam_999/{today}")
    
    print(f"[✓] Estrutura: {path}")
    
    if not path.exists():
        print(f"[✗] Pasta não existe")
        return False
    
    files = sorted([f.name for f in path.glob("*.mp4")])
    print(f"[{'✓' if len(files) > 0 else '✗'}] Arquivos: {len(files)}/24")
    
    for h in range(24):
        fname = f"{h:02d}.mp4"
        print(f"  [{'✓' if fname in files else '✗'}] {fname}")
    
    return len(files) == 24

def check_format():
    today = datetime.now().strftime("%Y-%m-%d")
    file = Path(f"/recordings/cam_999/{today}/00.mp4")
    
    if not file.exists():
        print("[✗] Arquivo 00.mp4 não existe")
        return False
    
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=codec_name:format=format_name",
         "-of", "json", str(file)],
        capture_output=True, text=True
    )
    
    try:
        data = json.loads(result.stdout)
        codec = data['streams'][0]['codec_name']
        fmt = data['format']['format_name']
        
        print(f"[{'✓' if codec == 'h264' else '✗'}] Codec: {codec}")
        print(f"[{'✓' if 'mp4' in fmt else '✗'}] Formato: {fmt}")
        return codec == 'h264'
    except:
        print("[✗] Erro ao verificar formato")
        return False

def check_duration():
    today = datetime.now().strftime("%Y-%m-%d")
    path = Path(f"/recordings/cam_999/{today}")
    
    if not path.exists():
        return
    
    files = sorted(path.glob("*.mp4"))[:3]
    
    for f in files:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration", "-of", "csv=p=0", str(f)],
            capture_output=True, text=True
        )
        
        try:
            dur_min = float(result.stdout.strip()) / 60
            status = "✓" if 55 <= dur_min <= 65 else "✗"
            print(f"  [{status}] {f.name}: {dur_min:.1f} min")
        except:
            print(f"  [✗] {f.name}: erro")

print("=" * 60)
print("SPRINT 1 - VALIDAÇÃO")
print("=" * 60)
print()

print("1. ESTRUTURA")
print("-" * 60)
check_structure()
print()

print("2. FORMATO E CODEC")
print("-" * 60)
check_format()
print()

print("3. DURAÇÃO")
print("-" * 60)
check_duration()
print()

print("=" * 60)
