"""
Script de teste para o serviço VOD HLS
"""
import requests
import json

BASE_URL = "http://localhost:8006"

def test_health():
    """Testa health check"""
    print("🔍 Testando /health...")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Status: {r.status_code}")
        print(f"   Response: {r.json()}\n")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}\n")
        return False

def test_debug():
    """Testa rota de debug"""
    print("🔍 Testando /vod/debug...")
    try:
        r = requests.get(f"{BASE_URL}/vod/debug", timeout=5)
        print(f"✅ Status: {r.status_code}")
        data = r.json()
        print(f"   Diretório: {data['recordings_dir']}")
        print(f"   Existe: {data['exists']}")
        print(f"   É diretório: {data['is_dir']}")
        print(f"   Conteúdo: {json.dumps(data['contents'], indent=2)}\n")
        return data
    except Exception as e:
        print(f"❌ Erro: {e}\n")
        return None

def test_recordings():
    """Testa listagem de gravações"""
    print("🔍 Testando /vod/recordings...")
    try:
        r = requests.get(f"{BASE_URL}/vod/recordings", timeout=5)
        print(f"✅ Status: {r.status_code}")
        data = r.json()
        print(f"   Response: {json.dumps(data, indent=2)}\n")
        return data
    except Exception as e:
        print(f"❌ Erro: {e}\n")
        return None

def test_playlist(camera_id, date):
    """Testa geração de playlist"""
    print(f"🔍 Testando /vod/playlist/{camera_id}/{date}/index.m3u8...")
    try:
        r = requests.get(f"{BASE_URL}/vod/playlist/{camera_id}/{date}/index.m3u8", timeout=5)
        print(f"✅ Status: {r.status_code}")
        if r.status_code == 200:
            lines = r.text.split('\n')
            print(f"   Linhas na playlist: {len(lines)}")
            print(f"   Primeiras 10 linhas:")
            for line in lines[:10]:
                print(f"     {line}")
        else:
            print(f"   Erro: {r.text}")
        print()
        return r.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}\n")
        return False

def test_segment(camera_id, date, filename):
    """Testa streaming de segmento"""
    print(f"🔍 Testando /vod/segment/{camera_id}/{date}/{filename}.ts...")
    try:
        # Primeiro testa HEAD
        r = requests.head(f"{BASE_URL}/vod/segment/{camera_id}/{date}/{filename}.ts", timeout=5)
        print(f"✅ HEAD Status: {r.status_code}")
        
        # Depois testa GET (apenas primeiros bytes)
        r = requests.get(f"{BASE_URL}/vod/segment/{camera_id}/{date}/{filename}.ts", 
                        stream=True, timeout=10)
        print(f"✅ GET Status: {r.status_code}")
        
        if r.status_code == 200:
            # Lê apenas os primeiros 1KB
            chunk = next(r.iter_content(1024))
            print(f"   Primeiros bytes recebidos: {len(chunk)} bytes")
            print(f"   Content-Type: {r.headers.get('content-type')}\n")
            return True
        else:
            print(f"   Erro: {r.text}\n")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}\n")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🎬 TESTE DO SERVIÇO VOD HLS")
    print("=" * 60 + "\n")
    
    # 1. Health check
    if not test_health():
        print("❌ Serviço não está respondendo. Verifique se está rodando.")
        exit(1)
    
    # 2. Debug
    debug_data = test_debug()
    
    # 3. Recordings
    recordings_data = test_recordings()
    
    # 4. Se houver gravações, testa playlist e segmento
    if recordings_data and recordings_data.get("recordings"):
        for camera_id, dates in recordings_data["recordings"].items():
            for date, info in dates.items():
                print(f"\n📹 Testando câmera {camera_id}, data {date}")
                print(f"   Arquivos: {info['count']}")
                
                # Testa playlist
                if test_playlist(camera_id, date):
                    # Testa primeiro segmento
                    first_file = info.get("first_file")
                    if first_file:
                        test_segment(camera_id, date, first_file)
                
                break  # Testa apenas a primeira data
            break  # Testa apenas a primeira câmera
    else:
        print("⚠️  Nenhuma gravação encontrada para testar playlist/segmento")
    
    print("\n" + "=" * 60)
    print("✅ TESTES CONCLUÍDOS")
    print("=" * 60)
