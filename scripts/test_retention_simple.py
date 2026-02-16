"""
Teste Mock de Retencao de Gravacoes
"""
import os
from datetime import datetime, timedelta
from pathlib import Path

RECORDINGS_BASE = Path("recordings")
TEST_CAMERAS = [
    {"id": 101, "name": "Camera_7dias", "retention_days": 7},
    {"id": 102, "name": "Camera_15dias", "retention_days": 15},
    {"id": 103, "name": "Camera_30dias", "retention_days": 30},
]

def create_mock_recording(camera_id, date, hour):
    date_str = date.strftime("%Y-%m-%d")
    hour_str = f"{hour:02d}-00-00"
    
    path = RECORDINGS_BASE / f"camera_{camera_id}" / date_str
    path.mkdir(parents=True, exist_ok=True)
    
    file_path = path / f"{hour_str}.mp4"
    file_path.write_text(f"Mock: Camera {camera_id} - {date_str} {hour_str}")
    
    timestamp = datetime.combine(date, datetime.min.time().replace(hour=hour)).timestamp()
    os.utime(file_path, (timestamp, timestamp))
    
    return file_path

def create_test_recordings():
    print("Criando gravacoes de teste...\n")
    
    today = datetime.now().date()
    
    for camera in TEST_CAMERAS:
        camera_id = camera["id"]
        retention = camera["retention_days"]
        
        print(f"Camera {camera['name']} (Retencao: {retention} dias)")
        
        # Gravacoes antigas (devem ser deletadas)
        old_date = today - timedelta(days=retention + 5)
        for hour in range(0, 24, 6):
            file_path = create_mock_recording(camera_id, old_date, hour)
            print(f"  [X] DEVE DELETAR: {file_path.relative_to(RECORDINGS_BASE)}")
        
        # Gravacoes no limite
        limit_date = today - timedelta(days=retention)
        for hour in range(0, 24, 6):
            file_path = create_mock_recording(camera_id, limit_date, hour)
            print(f"  [!] NO LIMITE: {file_path.relative_to(RECORDINGS_BASE)}")
        
        # Gravacoes recentes (devem ser mantidas)
        recent_date = today - timedelta(days=retention - 2)
        for hour in range(0, 24, 6):
            file_path = create_mock_recording(camera_id, recent_date, hour)
            print(f"  [OK] DEVE MANTER: {file_path.relative_to(RECORDINGS_BASE)}")
        
        print()

def verify_retention():
    print("\n" + "="*60)
    print("VERIFICACAO DE RETENCAO")
    print("="*60 + "\n")
    
    today = datetime.now().date()
    
    for camera in TEST_CAMERAS:
        camera_id = camera["id"]
        retention = camera["retention_days"]
        cutoff_date = today - timedelta(days=retention)
        
        print(f"Camera {camera['name']}")
        print(f"   Retencao: {retention} dias")
        print(f"   Data de corte: {cutoff_date}\n")
        
        camera_path = RECORDINGS_BASE / f"camera_{camera_id}"
        if not camera_path.exists():
            print("   Pasta nao encontrada\n")
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

if __name__ == "__main__":
    create_test_recordings()
    verify_retention()
    print("\nTeste concluido!")
