#!/usr/bin/env python3
"""Migra clips órfãos para o banco JSON"""
import json
import subprocess
from pathlib import Path
from datetime import datetime

CLIPS_DIR = Path("/clips")
DB_FILE = CLIPS_DIR / "clips_db.json"

def get_video_duration(file_path):
    """Obtém duração do vídeo usando ffprobe"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', str(file_path)],
            capture_output=True, text=True, timeout=5
        )
        return int(float(result.stdout.strip()))
    except:
        return 0

clips_db = {}

# Encontrar todos os MP4s
for mp4 in CLIPS_DIR.glob("*.mp4"):
    clip_id = mp4.stem
    if clip_id == "clips_db":
        continue
    
    stat = mp4.stat()
    duration = get_video_duration(mp4)
    
    clips_db[clip_id] = {
        "camera_id": 0,
        "start_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "end_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "status": "completed",
        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "file_size": stat.st_size,
        "duration": duration,
        "file_path": str(mp4)
    }
    print(f"Migrado: {clip_id} ({duration}s)")

# Salvar
with open(DB_FILE, 'w') as f:
    json.dump(clips_db, f, indent=2)

print(f"\n✅ {len(clips_db)} clips migrados para {DB_FILE}")
