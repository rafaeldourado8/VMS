import subprocess
import json
from pathlib import Path
from datetime import datetime

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def check_structure():
    """Verifica estrutura de pastas"""
    today = datetime.now().strftime("%Y-%m-%d")
    path = f"/recordings/cam_999/{today}"
    cmd = f'docker exec gtvision_mediamtx ls -1 {path} 2>nul'
    files = run_cmd(cmd).split('\n')
    
    expected = [f"{h:02d}.mp4" for h in range(24)]
    found = [f for f in files if f.endswith('.mp4')]
    
    print(f"[✓] Estrutura: /recordings/cam_999/{today}/")
    print(f"[{'✓' if len(found) > 0 else '✗'}] Arquivos encontrados: {len(found)}/24")
    
    for h in range(24):
        fname = f"{h:02d}.mp4"
        status = "✓" if fname in found else "✗"
        print(f"  [{status}] {fname}")
    
    return len(found) == 24

def check_format():
    """Verifica formato e codec"""
    today = datetime.now().strftime("%Y-%m-%d")
    file = f"/recordings/cam_999/{today}/00.mp4"
    
    cmd = f'docker exec gtvision_mediamtx ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,format=format_name -of json {file}'
    output = run_cmd(cmd)
    
    try:
        data = json.loads(output)
        codec = data['streams'][0]['codec_name']
        fmt = data['format']['format_name']
        
        print(f"[{'✓' if codec == 'h264' else '✗'}] Codec: {codec}")
        print(f"[{'✓' if 'mp4' in fmt else '✗'}] Formato: {fmt}")
        return codec == 'h264'
    except:
        print("[✗] Erro ao verificar formato")
        return False
    
def check_duration():
    """Verifica duração dos arquivos"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    for h in range(min(3, 24)):  # Testa primeiros 3 arquivos
        file = f"/recordings/cam_999/{today}/{h:02d}.mp4"
        cmd = f'docker exec gtvision_mediamtx ffprobe -v error -show_entries format=duration -of csv=p=0 {file}'
        duration = run_cmd(cmd)
        
        try:
            dur_min = float(duration) / 60
            status = "✓" if 55 <= dur_min <= 65 else "✗"
            print(f"  [{status}] {h:02d}.mp4: {dur_min:.1f} min")
        except:
            print(f"  [✗] {h:02d}.mp4: erro")

def check_logs():
    """Verifica logs de erro"""
    cmd = 'docker logs --tail 100 gtvision_mediamtx 2>&1 | findstr /I "error cam_999"'
    errors = run_cmd(cmd)
    
    has_errors = len(errors) > 0 and 'error' in errors.lower()
    print(f"[{'✗' if has_errors else '✓'}] Logs {'COM' if has_errors else 'SEM'} erros")
    
    if has_errors:
        print(f"  Erros encontrados:\n{errors[:200]}")
    
    return not has_errors

if __name__ == "__main__":
    print("=" * 60)
    print("SPRINT 1 - VALIDAÇÃO DE GRAVAÇÃO 24/7")
    print("=" * 60)
    print()
    
    print("1. ESTRUTURA DE ARQUIVOS")
    print("-" * 60)
    check_structure()
    print()
    
    print("2. FORMATO E CODEC")
    print("-" * 60)
    check_format()
    print()
    
    print("3. DURAÇÃO DOS ARQUIVOS")
    print("-" * 60)
    check_duration()
    print()
    
    print("4. LOGS DE ERRO")
    print("-" * 60)
    check_logs()
    print()
    
    print("=" * 60)
    print("VALIDAÇÃO CONCLUÍDA")
    print("=" * 60)
