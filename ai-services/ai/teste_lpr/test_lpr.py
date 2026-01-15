"""Teste LPR - Detecção de Placas em Imagens"""
import os
import sys
from pathlib import Path
from PIL import Image
import re

# Adicionar path do projeto
sys.path.append(str(Path(__file__).parent))
import utils_simple as utils

from ultralytics import YOLO

# Configuração
TEST_DIR = Path('/app/images')
IMAGES_DIR = TEST_DIR
RESULTS_DIR = Path('/app/results')
RESULTS_DIR.mkdir(exist_ok=True)

# Modelos
VEHICLE_MODEL = 'yolov8n.pt'
PLATE_MODEL = 'yolov8n.pt'

print("Teste LPR - Detecção de Placas")
print("=" * 50)

# Carregar modelos
print("\nCarregando modelos...")
vehicle_yolo = YOLO(VEHICLE_MODEL)
plate_yolo = YOLO(PLATE_MODEL)
print("Modelos carregados")

# Labels de veículos
CAR_LABELS = [
    utils.normalize_label('car'),
    utils.normalize_label('motorcycle'),
    utils.normalize_label('bus'),
    utils.normalize_label('truck')
]

def is_valid_plate(text: str) -> bool:
    """Valida se o texto parece uma placa Mercosul"""
    if len(text) < 7:
        return False
    
    # Padrão Mercosul: ABC1D23 ou ABC1234
    # Pelo menos 3 letras e 3 números
    letters = sum(c.isalpha() for c in text)
    numbers = sum(c.isdigit() for c in text)
    
    return letters >= 3 and numbers >= 3

# Processar imagens
image_files = list(IMAGES_DIR.glob('*.jpg')) + list(IMAGES_DIR.glob('*.png'))
image_files = [f for f in image_files if f.parent.name != 'results']

if not image_files:
    print("\nNenhuma imagem encontrada")
    sys.exit(1)

print(f"\nEncontradas {len(image_files)} imagens")
print("=" * 50)

total_detections = 0
best_detections = []

for img_path in image_files:
    print(f"\nProcessando: {img_path.name}")
    
    try:
        frame = Image.open(img_path)
    except Exception as e:
        print(f"  ERRO ao abrir imagem: {e}")
        continue
    
    # Detectar veículos
    num_vehicles, vehicle_boxes = utils.detect_with_yolo(vehicle_yolo, frame, False)
    print(f"  Veículos: {num_vehicles}")
    
    if num_vehicles == 0:
        continue
    
    image_best = None
    
    for i, vehicle_box in enumerate(vehicle_boxes):
        label = utils.normalize_label(vehicle_yolo.names[int(vehicle_box.cls)])
        if label not in CAR_LABELS:
            continue
        
        x_min, y_min, x_max, y_max = vehicle_box.xyxy.cpu().detach().numpy()[0]
        vehicle_img = frame.crop((x_min, y_min, x_max, y_max))
        
        num_plates, plate_boxes = utils.detect_with_yolo(plate_yolo, vehicle_img, False)
        
        if num_plates == 0:
            continue
        
        for j, plate_box in enumerate(plate_boxes):
            plate_img, plate_text = utils.read_license_plate(plate_box, vehicle_img, min_chars=7)
            
            if not is_valid_plate(plate_text):
                continue
            
            confidence = min(len(plate_text) / 7.0, 1.0)
            
            detection = {
                'image_name': img_path.stem,
                'plate': plate_text,
                'confidence': confidence,
                'vehicle_img': vehicle_img,
                'plate_img': plate_img
            }
            
            if image_best is None or confidence > image_best['confidence']:
                image_best = detection
            
            print(f"  PLACA: {plate_text} (confianca: {confidence:.0%})")
    
    if image_best:
        best_detections.append(image_best)
        total_detections += 1

print("\n" + "=" * 50)
print(f"Total de placas validas: {total_detections}")
print("\nSalvando melhores deteccoes...")
print("=" * 50)

for det in best_detections:
    plate_clean = det['plate'].replace(' ', '')
    result_name = f"{plate_clean}_{det['image_name']}"
    
    det['vehicle_img'].save(RESULTS_DIR / f"{result_name}_vehicle.jpg")
    det['plate_img'].save(RESULTS_DIR / f"{result_name}_plate.jpg")
    
    print(f"\n{det['image_name']}.jpg")
    print(f"  Placa: {det['plate']}")
    print(f"  Confianca: {det['confidence']:.0%}")
    print(f"  Salvo: {result_name}_*.jpg")

print("\n" + "=" * 50)
print(f"🎯 Total de placas detectadas: {total_detections}")
print(f"📁 Resultados salvos em: {RESULTS_DIR}")
print("=" * 50)
