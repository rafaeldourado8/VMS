"""
Simulador de Limpeza de Retenção
Testa a política de retenção sem deletar arquivos reais
"""
import os
from datetime import datetime, timedelta
from pathlib import Path

RECORDINGS_BASE = Path("../recordings")

def get_camera_retention(camera_id):
    """Simula busca de política de retenção do banco"""
    # Mock: mapeia IDs de teste para políticas
    retention_map = {
        101: 7,
        102: 15,
        103: 30,
    }
    return retention_map.get(camera_id, 30)

def simulate_cleanup(dry_run=True):
    """Simula limpeza de gravações antigas"""
    print("="*60)
    print("SIMULACAO DE LIMPEZA DE RETENCAO")
    print("="*60)
    print(f"Modo: {'DRY RUN (nao deleta)' if dry_run else 'DELETAR ARQUIVOS'}")
    print()
    
    today = datetime.now().date()
    total_deleted = 0
    total_size = 0
    
    # Procurar todas as câmeras
    for camera_folder in sorted(RECORDINGS_BASE.glob("camera_*")):
        if not camera_folder.is_dir():
            continue
        
        try:
            camera_id = int(camera_folder.name.split("_")[1])
        except (IndexError, ValueError):
            continue
        
        retention_days = get_camera_retention(camera_id)
        cutoff_date = today - timedelta(days=retention_days)
        
        print(f"Camera {camera_id}")
        print(f"   Retencao: {retention_days} dias")
        print(f"   Data de corte: {cutoff_date}")
        
        deleted_count = 0
        deleted_size = 0
        
        # Verificar cada pasta de data
        for date_folder in sorted(camera_folder.iterdir()):
            if not date_folder.is_dir():
                continue
            
            try:
                folder_date = datetime.strptime(date_folder.name, "%Y-%m-%d").date()
            except ValueError:
                continue
            
            # Verificar se deve deletar
            if folder_date < cutoff_date:
                files = list(date_folder.glob("*.mp4"))
                folder_size = sum(f.stat().st_size for f in files)
                
                print(f"   [X] DELETAR: {date_folder.name} ({len(files)} arquivos, {folder_size/1024/1024:.2f} MB)")
                
                if not dry_run:
                    import shutil
                    shutil.rmtree(date_folder)
                    print(f"      [OK] Deletado!")
                
                deleted_count += len(files)
                deleted_size += folder_size
            else:
                files = list(date_folder.glob("*.mp4"))
                print(f"   [OK] MANTER: {date_folder.name} ({len(files)} arquivos)")
        
        if deleted_count > 0:
            print(f"\n   Total: {deleted_count} arquivos, {deleted_size/1024/1024:.2f} MB")
        
        total_deleted += deleted_count
        total_size += deleted_size
        print()
    
    print("="*60)
    print("RESUMO")
    print("="*60)
    print(f"Total de arquivos {'que seriam deletados' if dry_run else 'deletados'}: {total_deleted}")
    print(f"Espaço {'que seria liberado' if dry_run else 'liberado'}: {total_size/1024/1024:.2f} MB")
    print()

if __name__ == "__main__":
    import sys
    
    dry_run = "--delete" not in sys.argv
    
    if not dry_run:
        print("\n[!] ATENCAO: Modo de delecao ativado!")
        print("Os arquivos serão REALMENTE deletados.\n")
        confirm = input("Digite 'SIM' para confirmar: ")
        if confirm != "SIM":
            print("Operação cancelada.")
            sys.exit(0)
    
    simulate_cleanup(dry_run=dry_run)
    
    if dry_run:
        print("\n[!] Para deletar os arquivos, execute:")
        print("   python test_retention_cleanup.py --delete")
