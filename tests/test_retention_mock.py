"""
Teste Mock de Retenção de Gravações
Simula gravações com 7, 15 e 30 dias para testar política de retenção
"""
import os
from datetime import datetime, timedelta
from pathlib import Path

# Configurações
RECORDINGS_BASE = Path("../recordings")
TEST_CAMERAS = [
    {"id": 101, "name": "Camera_7dias", "retention_days": 7},
    {"id": 102, "name": "Camera_15dias", "retention_days": 15},
    {"id": 103, "name": "Camera_30dias", "retention_days": 30},
]

def create_mock_recording(camera_id, date, hour):
    """Cria arquivo mock de gravação"""
    date_str = date.strftime("%Y-%m-%d")
    hour_str = f"{hour:02d}-00-00"
    
    path = RECORDINGS_BASE / f"camera_{camera_id}" / date_str
    path.mkdir(parents=True, exist_ok=True)
    
    file_path = path / f"{hour_str}.mp4"
    file_path.write_text(f"Mock recording: Camera {camera_id} - {date_str} {hour_str}")
    
    # Ajustar timestamp do arquivo para a data simulada
    timestamp = datetime.combine(date, datetime.min.time().replace(hour=hour)).timestamp()
    os.utime(file_path, (timestamp, timestamp))
    
    return file_path

def create_test_recordings():
    """Cria gravações de teste para cada câmera"""
    print("Criando gravacoes de teste...\n")
    
    today = datetime.now().date()
    
    for camera in TEST_CAMERAS:
        camera_id = camera["id"]
        retention = camera["retention_days"]
        
        print(f"[Camera] {camera['name']} (Retencao: {retention} dias)")
        
        # Criar gravações antigas (devem ser deletadas)
        old_date = today - timedelta(days=retention + 5)
        for hour in range(0, 24, 6):
            file_path = create_mock_recording(camera_id, old_date, hour)
            print(f"  [X] DEVE DELETAR: {file_path.relative_to(RECORDINGS_BASE)}")
        
        # Criar gravações no limite (devem ser deletadas)
        limit_date = today - timedelta(days=retention)
        for hour in range(0, 24, 6):
            file_path = create_mock_recording(camera_id, limit_date, hour)
            print(f"  [!] NO LIMITE: {file_path.relative_to(RECORDINGS_BASE)}")
        
        # Criar gravações recentes (devem ser mantidas)
        recent_date = today - timedelta(days=retention - 2)
        for hour in range(0, 24, 6):
            file_path = create_mock_recording(camera_id, recent_date, hour)
            print(f"  [OK] DEVE MANTER: {file_path.relative_to(RECORDINGS_BASE)}")
        
        # Criar gravações de hoje (devem ser mantidas)
        for hour in range(0, 24, 6):
            file_path = create_mock_recording(camera_id, today, hour)
            print(f"  [OK] DEVE MANTER: {file_path.relative_to(RECORDINGS_BASE)}")
        
        print()

def verify_retention():
    """Verifica quais arquivos devem ser deletados"""
    print("\n" + "="*60)
    print("VERIFICACAO DE RETENCAO")
    print("="*60 + "\n")
    
    today = datetime.now().date()
    
    for camera in TEST_CAMERAS:
        camera_id = camera["id"]
        retention = camera["retention_days"]
        cutoff_date = today - timedelta(days=retention)
        
        print(f"[Camera] {camera['name']}")
        print(f"   Retencao: {retention} dias")
        print(f"   Data de corte: {cutoff_date}")
        print(f"   Deletar arquivos antes de: {cutoff_date}\n")
        
        camera_path = RECORDINGS_BASE / f"camera_{camera_id}"
        if not camera_path.exists():
            print("   [!] Pasta nao encontrada\n")
            continue
        
        to_delete = []
        to_keep = []
        
        for date_folder in sorted(camera_path.iterdir()):
            if not date_folder.is_dir():
                continue
            
            try:
                folder_date = datetime.strptime(date_folder.name, "%Y-%m-%d").date()
                
                if folder_date < cutoff_date:
                    to_delete.append(date_folder)
                else:
                    to_keep.append(date_folder)
            except ValueError:
                continue
        
        print(f"   [X] Para deletar: {len(to_delete)} pastas")
        for folder in to_delete:
            file_count = len(list(folder.glob("*.mp4")))
            print(f"      - {folder.name} ({file_count} arquivos)")
        
        print(f"\n   [OK] Para manter: {len(to_keep)} pastas")
        for folder in to_keep:
            file_count = len(list(folder.glob("*.mp4")))
            print(f"      - {folder.name} ({file_count} arquivos)")
        
        print()

def cleanup_test_data():
    """Remove dados de teste"""
    print("\n" + "="*60)
    print("LIMPEZA DE DADOS DE TESTE")
    print("="*60 + "\n")
    
    for camera in TEST_CAMERAS:
        camera_path = RECORDINGS_BASE / f"camera_{camera['id']}"
        if camera_path.exists():
            import shutil
            shutil.rmtree(camera_path)
            print(f"[OK] Removido: {camera_path}")
    
    print("\nLimpeza concluida!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        cleanup_test_data()
    else:
        create_test_recordings()
        verify_retention()
        
        print("\n" + "="*60)
        print("PRÓXIMOS PASSOS")
        print("="*60)
        print("\n1. Execute o serviço de limpeza de retenção")
        print("2. Verifique se os arquivos foram deletados corretamente")
        print("3. Execute 'python test_retention_mock.py cleanup' para limpar\n")
