#!/usr/bin/env python3
"""
Indexa gravações do disco no banco de dados PostgreSQL
"""
import os
import psycopg2
from pathlib import Path
from datetime import datetime
import subprocess

# Configuração do banco
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'gtvision_db',
    'user': 'gtvision_user',
    'password': 'your-strong-password-here'
}

RECORDINGS_PATH = Path('d:/VMS/recordings')

def get_video_duration(file_path):
    """Obtém duração do vídeo usando ffprobe"""
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries',
            'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
            str(file_path)
        ], capture_output=True, text=True, timeout=5)
        return int(float(result.stdout.strip()))
    except:
        return 60  # Default 60s

def index_recordings():
    """Indexa todos os arquivos MP4 no banco"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    indexed = 0
    skipped = 0
    
    for camera_dir in RECORDINGS_PATH.glob('camera_*'):
        camera_id = int(camera_dir.name.split('_')[1])
        
        for date_dir in camera_dir.glob('*'):
            if not date_dir.is_dir():
                continue
                
            for mp4_file in date_dir.glob('*.mp4'):
                file_path = f"/recordings/{camera_dir.name}/{date_dir.name}/{mp4_file.name}"
                
                # Verifica se já existe
                cur.execute("SELECT id FROM recording_segments WHERE file_path = %s", (file_path,))
                if cur.fetchone():
                    skipped += 1
                    continue
                
                # Parse do timestamp do nome do arquivo (HH-MM-SS.mp4)
                time_str = mp4_file.stem  # Remove .mp4
                try:
                    hour, minute, second = map(int, time_str.split('-'))
                    date_obj = datetime.strptime(date_dir.name, '%Y-%m-%d')
                    start_time = date_obj.replace(hour=hour, minute=minute, second=second)
                except:
                    print(f"⚠️  Ignorando arquivo com nome inválido: {mp4_file}")
                    continue
                
                duration = get_video_duration(mp4_file)
                end_time = start_time.replace(second=start_time.second + duration)
                file_size = mp4_file.stat().st_size
                
                # Insere no banco
                cur.execute("""
                    INSERT INTO recording_segments 
                    (camera_id, file_path, start_time, end_time, duration_seconds, file_size_bytes, processed)
                    VALUES (%s, %s, %s, %s, %s, %s, true)
                    ON CONFLICT (file_path) DO NOTHING
                """, (camera_id, file_path, start_time, end_time, duration, file_size))
                
                indexed += 1
                print(f"✅ Indexado: camera_{camera_id} - {date_dir.name}/{mp4_file.name}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"\n📊 Resultado:")
    print(f"   ✅ Indexados: {indexed}")
    print(f"   ⏭️  Ignorados: {skipped}")

if __name__ == '__main__':
    print("🔍 Indexando gravações do disco...\n")
    index_recordings()
