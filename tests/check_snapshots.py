import os
import json
from pathlib import Path

snapshot_dir = Path("./snapshots")

print("=== VERIFICANDO SNAPSHOTS ===\n")

if not snapshot_dir.exists():
    print("✗ Diretório de snapshots não existe")
    exit(1)

cameras = list(snapshot_dir.glob("cam_*"))

if not cameras:
    print("✗ Nenhuma câmera encontrada")
    exit(0)

print(f"✓ Encontradas {len(cameras)} câmeras\n")

for cam_dir in sorted(cameras):
    print(f"📷 {cam_dir.name}")
    detections = list(cam_dir.glob("*"))
    
    if not detections:
        print("   └─ Nenhuma detecção")
        continue
    
    print(f"   └─ {len(detections)} detecções")
    
    for det_dir in sorted(detections)[-5:]:  # Últimas 5 detecções
        metadata_file = det_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                metadata = json.load(f)
            
            vehicle_file = det_dir / "vehicle.jpg"
            plate_file = det_dir / "plate.jpg"
            
            print(f"      ├─ {det_dir.name}")
            print(f"      │  ├─ Tipo: {metadata.get('vehicle_type', 'N/A')}")
            print(f"      │  ├─ Confiança: {metadata.get('confidence', 0):.2f}")
            print(f"      │  ├─ Timestamp: {metadata.get('timestamp', 'N/A')}")
            print(f"      │  ├─ Vehicle.jpg: {'✓' if vehicle_file.exists() else '✗'}")
            print(f"      │  └─ Plate.jpg: {'✓' if plate_file.exists() else '✗'}")

print("\n=== FIM ===")
