#!/usr/bin/env python3
"""
Script para testar criação de clips e verificar se não estão corrompidos
"""
import requests
import time
import subprocess
import sys
from datetime import datetime, timedelta

CLIPS_SERVICE = "http://localhost:8004"

def test_clip_creation():
    """Testa criação de um clip"""
    
    # Usar horário de agora menos 1 hora para garantir que existe gravação
    end_time = datetime.now()
    start_time = end_time - timedelta(seconds=30)  # Clip de 30 segundos
    
    print(f"🎬 Criando clip de teste...")
    print(f"   Câmera: 1")
    print(f"   Início: {start_time.isoformat()}")
    print(f"   Fim: {end_time.isoformat()}")
    
    # Criar clip
    response = requests.post(
        f"{CLIPS_SERVICE}/clips/create",
        json={
            "camera_id": 1,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "quality": "medium"
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Erro ao criar clip: {response.text}")
        return False
    
    data = response.json()
    clip_id = data["id"]
    print(f"✅ Clip criado: {clip_id}")
    print(f"   Status: {data['status']}")
    
    # Aguardar processamento
    print("\n⏳ Aguardando processamento...")
    max_attempts = 60
    for i in range(max_attempts):
        time.sleep(2)
        
        status_response = requests.get(f"{CLIPS_SERVICE}/clips/{clip_id}")
        if status_response.status_code != 200:
            print(f"❌ Erro ao verificar status: {status_response.text}")
            return False
        
        status_data = status_response.json()
        current_status = status_data["status"]
        
        print(f"   [{i+1}/{max_attempts}] Status: {current_status}")
        
        if current_status == "completed":
            print(f"\n✅ Clip processado com sucesso!")
            print(f"   Tamanho: {status_data.get('file_size', 0) / 1024 / 1024:.2f} MB")
            print(f"   Duração: {status_data.get('duration', 0)}s")
            
            # Verificar integridade do arquivo
            print("\n🔍 Verificando integridade do vídeo...")
            download_url = f"{CLIPS_SERVICE}/clips/{clip_id}/download"
            
            # Baixar clip temporariamente
            clip_response = requests.get(download_url, stream=True)
            if clip_response.status_code != 200:
                print(f"❌ Erro ao baixar clip: {clip_response.status_code}")
                return False
            
            temp_file = f"temp_clip_{clip_id}.mp4"
            with open(temp_file, 'wb') as f:
                for chunk in clip_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verificar com FFprobe
            try:
                result = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_format", "-show_streams", temp_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    print("✅ Vídeo válido e não corrompido!")
                    print(f"\n📊 Informações do vídeo:")
                    print(result.stdout[:500])
                    
                    # Limpar arquivo temporário
                    import os
                    os.remove(temp_file)
                    return True
                else:
                    print(f"❌ Vídeo corrompido!")
                    print(f"   Erro: {result.stderr}")
                    return False
                    
            except subprocess.TimeoutExpired:
                print("❌ Timeout ao verificar vídeo")
                return False
            except FileNotFoundError:
                print("⚠️  FFprobe não encontrado, pulando verificação de integridade")
                print("   Instale FFmpeg para verificação completa")
                return True
                
        elif current_status == "failed":
            print(f"\n❌ Falha ao processar clip!")
            print(f"   Erro: {status_data.get('error', 'Desconhecido')}")
            return False
    
    print(f"\n❌ Timeout: clip não foi processado em {max_attempts * 2}s")
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTE DE CRIAÇÃO DE CLIPS")
    print("=" * 60)
    print()
    
    try:
        success = test_clip_creation()
        print("\n" + "=" * 60)
        if success:
            print("✅ TESTE PASSOU!")
            sys.exit(0)
        else:
            print("❌ TESTE FALHOU!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
