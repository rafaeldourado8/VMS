import requests
import json
import sys

MEDIAMTX_API = "http://localhost:9997"
AUTH = ("mediamtx_api_user", "GtV!sionMed1aMTX$2025")

def disable_recording():
    try:
        # Lista todos os paths
        resp = requests.get(f"{MEDIAMTX_API}/v3/paths/list", auth=AUTH, timeout=5)
        paths = resp.json().get("items", [])
        
        print(f"Encontrados {len(paths)} paths")
        
        for path in paths:
            name = path["name"]
            
            # Pega config completa
            resp = requests.get(f"{MEDIAMTX_API}/v3/config/paths/get/{name}", auth=AUTH, timeout=5)
            if resp.status_code != 200:
                continue
                
            config = resp.json()
            is_recording = config.get("record", False)
            
            if is_recording:
                print(f"❌ {name} está gravando - DESABILITANDO...")
                
                # Desabilita gravação
                patch_config = {"record": False}
                resp = requests.patch(
                    f"{MEDIAMTX_API}/v3/config/paths/patch/{name}",
                    json=patch_config,
                    auth=AUTH,
                    timeout=5
                )
                
                if resp.status_code in [200, 204]:
                    print(f"✅ {name} - gravação desabilitada")
                else:
                    print(f"⚠️ {name} - erro: {resp.status_code} - {resp.text}")
            else:
                print(f"✅ {name} - já está sem gravação")
        
        return True
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

if __name__ == "__main__":
    success = disable_recording()
    sys.exit(0 if success else 1)
