"""
Script para coletar imagens de placas Mercosul para treinamento
Monitora snapshots e separa placas válidas para dataset
"""
import os
import json
import shutil
from pathlib import Path
import re

SNAPSHOT_DIR = Path("/app/snapshots")
TRAINING_DIR = Path("/app/training_data/mercosul")
TRAINING_DIR.mkdir(parents=True, exist_ok=True)

def validate_mercosul(text):
    """Valida padrão Mercosul: ABC1D23"""
    if not text or len(text) != 7:
        return False
    return bool(re.match(r'^[A-Z]{3}[0-9][A-Z][0-9]{2}$', text))

def collect_plates():
    """Coleta placas válidas dos snapshots"""
    collected = 0
    
    for cam_dir in SNAPSHOT_DIR.glob("cam_*"):
        if cam_dir.name == "preview":
            continue
            
        for snap_dir in cam_dir.glob("*_*"):
            metadata_file = snap_dir / "metadata.json"
            plate_file = snap_dir / "plate.jpg"
            
            if not metadata_file.exists() or not plate_file.exists():
                continue
            
            with open(metadata_file) as f:
                meta = json.load(f)
            
            plate_text = meta.get("plate_text", "")
            if validate_mercosul(plate_text):
                # Copia para dataset de treinamento
                dest = TRAINING_DIR / f"{plate_text}_{meta['uuid']}.jpg"
                if not dest.exists():
                    shutil.copy(plate_file, dest)
                    collected += 1
                    print(f"✓ {plate_text}")
    
    print(f"\n{collected} placas Mercosul coletadas em {TRAINING_DIR}")
    print(f"Total no dataset: {len(list(TRAINING_DIR.glob('*.jpg')))}")

if __name__ == "__main__":
    collect_plates()
