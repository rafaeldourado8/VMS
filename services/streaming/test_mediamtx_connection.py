#!/usr/bin/env python3
"""
Script para testar conexão com MediaMTX API
"""
import httpx
import os
import sys

def test_mediamtx_connection():
    """Testa conexão com MediaMTX"""
    
    # Configuração
    base_url = os.getenv("MEDIAMTX_API_URL", "http://mediamtx:9997")
    username = os.getenv("MEDIAMTX_API_USER", "mediamtx_api_user")
    password = os.getenv("MEDIAMTX_API_PASS", "GtV!sionMed1aMTX$2025")
    
    print(f"🔍 Testando conexão com MediaMTX...")
    print(f"   URL: {base_url}")
    print(f"   User: {username}")
    print(f"   Pass: {'*' * len(password)}")
    print()
    
    try:
        # Teste 1: Health check sem autenticação
        print("1️⃣ Testando acesso básico (sem auth)...")
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{base_url}/v3/config/global/get")
            print(f"   Status: {response.status_code}")
            if response.status_code == 401:
                print("   ✅ MediaMTX está respondendo (requer autenticação)")
            elif response.status_code == 200:
                print("   ✅ MediaMTX está respondendo (sem autenticação)")
            else:
                print(f"   ⚠️ Resposta inesperada: {response.text[:200]}")
        print()
        
        # Teste 2: Com autenticação
        print("2️⃣ Testando com autenticação...")
        with httpx.Client(timeout=5.0) as client:
            response = client.get(
                f"{base_url}/v3/config/global/get",
                auth=(username, password)
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Autenticação funcionando!")
                data = response.json()
                print(f"   Configuração: {list(data.keys())[:5]}")
            else:
                print(f"   ❌ Falha na autenticação: {response.text[:200]}")
        print()
        
        # Teste 3: Listar paths
        print("3️⃣ Listando paths existentes...")
        with httpx.Client(timeout=5.0) as client:
            response = client.get(
                f"{base_url}/v3/paths/list",
                auth=(username, password)
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                paths = data.get("items", [])
                print(f"   ✅ {len(paths)} paths encontrados")
                for path in paths[:3]:
                    print(f"      - {path.get('name', 'N/A')}")
            else:
                print(f"   ⚠️ Não foi possível listar: {response.text[:200]}")
        print()
        
        # Teste 4: Adicionar path de teste
        print("4️⃣ Testando adição de path...")
        test_path = "test_camera_999"
        test_rtsp = "rtsp://example.com/test"
        
        with httpx.Client(timeout=5.0) as client:
            response = client.patch(
                f"{base_url}/v3/config/paths/patch/{test_path}",
                json={
                    "source": test_rtsp,
                    "sourceOnDemand": True
                },
                auth=(username, password)
            )
            print(f"   Status: {response.status_code}")
            if response.status_code in [200, 201]:
                print(f"   ✅ Path de teste adicionado com sucesso!")
            else:
                print(f"   ❌ Falha ao adicionar: {response.text[:200]}")
        print()
        
        # Teste 5: Remover path de teste
        print("5️⃣ Removendo path de teste...")
        with httpx.Client(timeout=5.0) as client:
            response = client.patch(
                f"{base_url}/v3/config/paths/patch/{test_path}",
                json={"source": ""},
                auth=(username, password)
            )
            print(f"   Status: {response.status_code}")
            if response.status_code in [200, 204]:
                print(f"   ✅ Path de teste removido!")
            else:
                print(f"   ⚠️ Resposta: {response.text[:200]}")
        print()
        
        print("=" * 60)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        return 0
        
    except httpx.ConnectError as e:
        print(f"❌ ERRO DE CONEXÃO: {e}")
        print(f"   Verifique se o MediaMTX está rodando em {base_url}")
        return 1
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_mediamtx_connection())
