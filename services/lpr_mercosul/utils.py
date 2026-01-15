"""Utils - Adapted from alpr-yolov8-python-ocr"""
import io
import os
import cv2
import imutils
import numpy as np
import concurrent.futures
import pytesseract
from PIL import Image
from skimage.filters import threshold_local
from ultralytics import YOLO


def detect_with_yolo(model: YOLO, image: Image, verbose: bool = False):
    """Detect objects with YOLO"""
    result = model.predict(image, verbose=verbose)[0]
    return len(result.boxes), result.boxes


def normalize_label(label: str) -> str:
    """Normalize YOLO label"""
    return label.strip().lower()


def clean_plate_into_contours(plate_img: np.ndarray, fixed_width: int) -> np.ndarray:
    """Preprocess plate image for OCR"""
    plate_img = cv2.GaussianBlur(plate_img, (11, 11), 0)
    V = cv2.split(cv2.cvtColor(plate_img, cv2.COLOR_BGR2HSV))[2]
    T = threshold_local(V, 99, offset=5, method='gaussian')
    thresh = (V > T).astype('uint8') * 255
    thresh = cv2.bitwise_not(thresh)
    plate_img = imutils.resize(plate_img, width=fixed_width)
    thresh = imutils.resize(thresh, width=fixed_width)
    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_DILATE, kernel)
    return thresh


def get_letter_rectangles(iwl):
    """Extract letter bounding boxes from contours"""
    contours, _ = cv2.findContours(iwl, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    rectangles = []
    
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if h < (iwl.shape[0] / 5) or w > (iwl.shape[1] / 5):
            continue
        rectangles.append([x, y, w, h])
    
    # Remove nested rectangles
    final_rect = []
    for (x, y, w, h) in rectangles:
        is_nested = any(
            x > x2 and y > y2 and x + w < x2 + w2 and y + h < y2 + h2
            for (x2, y2, w2, h2) in rectangles
        )
        if not is_nested:
            final_rect.append([x, y, w, h])
    
    final_rect.sort()
    return final_rect


def read_license_plate(box, vehicle_image: Image, min_chars: int = 4) -> tuple:
    """Read license plate from vehicle image"""
    # Crop plate
    x_min, y_min, x_max, y_max = box.xyxy.cpu().detach().numpy()[0]
    width = x_max - x_min
    height = y_max - y_min
    
    # Resize for better OCR
    boost = 500 / width
    new_width = int(width * boost)
    new_height = int(height * boost)
    
    plate_img = vehicle_image.crop((x_min, y_min, x_max, y_max)).convert('L').resize((new_width, new_height))
    
    # Preprocess
    plate_array = cv2.cvtColor(np.array(plate_img), cv2.COLOR_GRAY2BGR)
    iwl_bb = clean_plate_into_contours(plate_array, 500)
    iwl_wb = cv2.bitwise_not(iwl_bb)
    
    # Get letters
    letter_rects = get_letter_rectangles(iwl_wb)
    
    if len(letter_rects) < min_chars:
        return plate_img, ""
    
    # OCR each letter
    iwl_wb_pil = Image.fromarray(iwl_wb, mode='L')
    
    def process_letter(args):
        i, (x, y, w, h) = args
        letter = iwl_wb_pil.crop((x, y, x + w, y + h))
        padded = Image.new('L', (letter.width + 40, letter.height + 40), 'white')
        padded.paste(letter, (20, 20))
        
        char = pytesseract.image_to_string(
            padded,
            lang='eng',
            config='--psm 13 --dpi 96 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        )
        return char.replace('O', '0').strip()
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(process_letter, enumerate(letter_rects)))
    
    plate_text = ''.join(results).strip()
    return plate_img, plate_text


def img_to_bytes(image: Image, format='JPEG') -> bytes:
    """Convert PIL Image to bytes"""
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    return buffer.getvalue()
