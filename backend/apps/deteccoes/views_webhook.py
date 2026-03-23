"""
Webhook async para receber push de cameras Intelbras/Hikvision com ALPR.

Suporta:
- Intelbras V1.13 Funcao Push (JSON com base64 binario)
- Hikvision ISAPI (XML com event notification)
- JSON generico (formato simples)
- Multipart com imagens
- KeepAlive de ambas as marcas

Projetado para alta disponibilidade com 20+ cameras simultaneas.
"""

import os
import re
import uuid
import base64
import logging
from datetime import datetime
from io import BytesIO

from django.conf import settings
from django.db import IntegrityError
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser, BaseParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from adrf.decorators import api_view
from rest_framework.decorators import permission_classes, parser_classes

from asgiref.sync import sync_to_async
from django.core.cache import cache as django_cache
from apps.cameras.models import Camera
from apps.deteccoes.models_lpr import LPRDetection

logger = logging.getLogger(__name__)

UPLOAD_DIR = os.path.join(settings.BASE_DIR, 'media', 'detections')

# Wrappers async para cache (django cache nao e async nativo)
cache_get = sync_to_async(django_cache.get)
cache_set = sync_to_async(django_cache.set)


# ============================================================
# Parsers customizados para aceitar qualquer Content-Type
# ============================================================

class RawParser(BaseParser):
    """Parser que aceita application/octet-stream e retorna bytes raw."""
    media_type = 'application/octet-stream'

    def parse(self, stream, media_type=None, parser_context=None):
        return stream.read()


class XMLParser(BaseParser):
    """Parser para XML (Hikvision ISAPI envia application/xml)."""
    media_type = 'application/xml'

    def parse(self, stream, media_type=None, parser_context=None):
        return stream.read()


class TextXMLParser(BaseParser):
    """Parser para text/xml (variante do XML)."""
    media_type = 'text/xml'

    def parse(self, stream, media_type=None, parser_context=None):
        return stream.read()


class CatchAllParser(BaseParser):
    """Parser fallback que aceita qualquer content-type nao mapeado."""
    media_type = '*/*'

    def parse(self, stream, media_type=None, parser_context=None):
        return stream.read()


ALL_PARSERS = [JSONParser, MultiPartParser, FormParser, XMLParser, TextXMLParser, RawParser, CatchAllParser]


# ============================================================
# Utilidades para salvar imagens
# ============================================================

def save_image(image_data, prefix="plate"):
    """Salva imagem de deteccao no disco. Aceita file upload ou bytes."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"{prefix}_{uuid.uuid4().hex[:12]}.jpg"
    filepath = os.path.join(UPLOAD_DIR, filename)

    if isinstance(image_data, bytes):
        with open(filepath, 'wb') as f:
            f.write(image_data)
    else:
        with open(filepath, 'wb') as f:
            for chunk in image_data.chunks():
                f.write(chunk)

    return f"detections/{filename}"


save_image_async = sync_to_async(save_image)


# ============================================================
# Parser binario Intelbras V1.13
# ============================================================

def extract_strings_from_binary(raw_bytes, min_length=3):
    """Extrai strings legiveis de dados binarios."""
    strings = []
    current = []
    current_start = 0
    for i, b in enumerate(raw_bytes):
        if 32 <= b <= 126:
            if not current:
                current_start = i
            current.append(chr(b))
        else:
            if len(current) >= min_length:
                strings.append((current_start, ''.join(current)))
            current = []
    if len(current) >= min_length:
        strings.append((current_start, ''.join(current)))
    return strings


def parse_intelbras_binary(b64_content):
    """
    Decodifica o formato proprietario Intelbras V1.13.
    Os dados da placa estao embutidos no header do JPEG como campos binarios.
    """
    result = {
        'plate_text': '',
        'confidence': 0.0,
        'vehicle_brand': '',
        'vehicle_model': '',
        'vehicle_color': '',
        'vehicle_type': 'unknown',
        'vehicle_year': None,
        'city': '',
        'direction': '',
        'trigger_source': 'intelbras_push',
        'device_id': '',
        'timestamp': timezone.now(),
        'image_data': None,
    }

    try:
        # Decodificar base64
        padding = 4 - len(b64_content) % 4
        if padding != 4:
            b64_content += '=' * padding
        raw = base64.b64decode(b64_content)

        # Extrair strings legiveis do header binario
        strings = extract_strings_from_binary(raw[:2048], min_length=3)

        for offset, text in strings:
            logger.debug(f"  Binary string at {offset}: '{text}'")

            # Timestamp (formato: 2026-03-22 21:37:58)
            if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', text):
                try:
                    result['timestamp'] = datetime.strptime(text, '%Y-%m-%d %H:%M:%S')
                    result['timestamp'] = timezone.make_aware(result['timestamp'])
                except (ValueError, TypeError):
                    pass

            # Placa brasileira (ABC1D23 ou ABC1234)
            text_clean = text.strip().upper()
            plate_match = re.fullmatch(r'[A-Z]{3}\d[A-Z0-9]\d{2}', text_clean)
            if plate_match and not result['plate_text']:
                result['plate_text'] = plate_match.group(0)
            elif not result['plate_text']:
                plate_search = re.search(r'(?:^|[\s\-])([A-Z]{3}\d[A-Z0-9]\d{2})(?:$|[\s\-])', text_clean)
                if plate_search:
                    result['plate_text'] = plate_search.group(1)

            text_lower = text.lower()

            # Direcao
            if not result['direction']:
                direction_keywords = ['norte', 'sul', 'leste', 'oeste', 'north', 'south', 'east', 'west',
                                      'entrada', 'saida']
                for kw in direction_keywords:
                    if kw in text_lower:
                        result['direction'] = text
                        break

            # Tipo de veiculo
            event_patterns = [
                (r'\bcar\b', 'car'), (r'\bvehicle\b', 'car'), (r'\bautomovel\b', 'car'),
                (r'\bmoto\b', 'motorcycle'), (r'\bmotorcycle\b', 'motorcycle'),
                (r'\btruck\b', 'truck'), (r'\bcaminhao\b', 'truck'),
                (r'\bbus\b', 'bus'), (r'\bonibus\b', 'bus'),
            ]
            for pattern, vtype in event_patterns:
                if re.search(pattern, text_lower):
                    result['vehicle_type'] = vtype
                    break

            # IP da camera
            ip_match = re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', text)
            if ip_match:
                if not result.get('device_ip'):
                    result['device_ip'] = text

            # Serial do dispositivo (ex: 9OHM1400095CU)
            if (len(text) >= 8
                and re.fullmatch(r'[A-Z0-9]+', text.upper())
                and not ip_match
                and not re.match(r'\d{4}-', text)
                and text.upper() != result.get('plate_text', '').upper()):
                result['device_id'] = text

        # ============================================================
        # Extrair campos de offsets fixos do COM segment V1.13
        # O COM marker (ff fe) começa no offset 86, dados em offset 90+
        # ============================================================
        com_start = raw.find(b'\xff\xfe')
        if com_start >= 0:
            com_data_start = com_start + 4  # skip ff fe + 2 bytes length

            # Confianca: offset fixo 161 (= com_data_start + 71)
            conf_offset = com_data_start + 71
            if conf_offset < len(raw):
                conf_val = raw[conf_offset]
                if 1 <= conf_val <= 100:
                    result['confidence'] = conf_val / 100.0

            # Bounding box da placa: offset 393+ (little-endian int32)
            bbox_base = com_data_start + 303  # = offset 393
            if bbox_base + 16 <= len(raw):
                import struct
                try:
                    bbox_x = struct.unpack_from('<I', raw, bbox_base)[0]
                    bbox_y = struct.unpack_from('<I', raw, bbox_base + 4)[0]
                    bbox_w = struct.unpack_from('<I', raw, bbox_base + 8)[0]
                    bbox_h = struct.unpack_from('<I', raw, bbox_base + 12)[0]
                    if 0 < bbox_x < 10000 and 0 < bbox_y < 10000 and 0 < bbox_w < 5000 and 0 < bbox_h < 5000:
                        result['bbox'] = [bbox_x, bbox_y, bbox_w, bbox_h]
                except (struct.error, ValueError):
                    pass

            # Cor do veiculo: Intelbras usa codigo numerico em offsets ~170-200
            # Codigos: 0=desconhecido, 1=branco, 2=cinza, 3=amarelo, 4=laranja,
            #          5=marrom, 6=vermelho, 7=rosa, 8=roxo, 9=azul, 10=verde, 11=ciano, 12=preto
            color_map = {
                1: 'Branco', 2: 'Cinza', 3: 'Amarelo', 4: 'Laranja',
                5: 'Marrom', 6: 'Vermelho', 7: 'Rosa', 8: 'Roxo',
                9: 'Azul', 10: 'Verde', 11: 'Ciano', 12: 'Preto',
            }
            # Testar varios offsets possiveis para cor (varia por firmware)
            for color_offset in [com_data_start + 80, com_data_start + 82, com_data_start + 84]:
                if color_offset < len(raw):
                    val = raw[color_offset]
                    if val in color_map:
                        result['vehicle_color'] = color_map[val]
                        break

            # Tipo de veiculo (codigo numerico)
            # 0=desconhecido, 1=carro, 2=van, 3=caminhao, 4=onibus, 5=moto
            vtype_map = {1: 'car', 2: 'van', 3: 'truck', 4: 'bus', 5: 'motorcycle'}
            for vtype_offset in [com_data_start + 86, com_data_start + 88]:
                if vtype_offset < len(raw):
                    val = raw[vtype_offset]
                    if val in vtype_map:
                        result['vehicle_type'] = vtype_map[val]
                        break

        # Fallback confianca
        if result['confidence'] == 0.0 and result['plate_text']:
            result['confidence'] = 0.85

        # A imagem JPEG comeca no marcador FFD8 (apos o COM segment)
        # Procurar o segundo FFD8 se o primeiro e o inicio do arquivo com metadados
        jpeg_start = raw.find(b'\xff\xd8')
        if jpeg_start >= 0:
            result['image_data'] = raw[jpeg_start:]
        else:
            result['image_data'] = raw

    except Exception as e:
        logger.error(f"Erro ao decodificar binario Intelbras: {e}")

    return result


# ============================================================
# Parser Hikvision ISAPI XML
# ============================================================

def parse_hikvision_xml(xml_bytes):
    """
    Parseia evento ISAPI/ANPR do Hikvision.
    O Hikvision envia XML com <EventNotificationAlert> ou <ANPR>.
    """
    import defusedxml.ElementTree as ET

    result = {
        'plate_text': '',
        'confidence': 0.0,
        'vehicle_brand': '',
        'vehicle_model': '',
        'vehicle_color': '',
        'vehicle_type': 'unknown',
        'vehicle_year': None,
        'city': '',
        'direction': '',
        'trigger_source': 'hikvision_isapi',
        'device_id': '',
        'timestamp': timezone.now(),
        'image_data': None,
    }

    try:
        if isinstance(xml_bytes, str):
            xml_bytes = xml_bytes.encode('utf-8')

        # Remover BOM se presente
        if xml_bytes.startswith(b'\xef\xbb\xbf'):
            xml_bytes = xml_bytes[3:]

        root = ET.fromstring(xml_bytes)

        # Remover namespace para facilitar busca
        ns = ''
        if root.tag.startswith('{'):
            ns = root.tag.split('}')[0] + '}'

        def find_text(elem, tag, default=''):
            el = elem.find(f'{ns}{tag}')
            if el is None:
                # Tentar sem namespace
                el = elem.find(tag)
            return el.text.strip() if el is not None and el.text else default

        # Placa — buscar em varios caminhos possiveis
        plate = ''
        for path in [
            './/ANPR/licensePlate',
            './/LicensePlate/plateNumber',
            './/licensePlate',
            './/plateNumber',
            f'.//{ns}ANPR/{ns}licensePlate',
            f'.//{ns}licensePlate',
            f'.//{ns}plateNumber',
        ]:
            el = root.find(path)
            if el is not None and el.text:
                plate = el.text.strip().upper()
                break

        result['plate_text'] = plate

        # Confianca
        for path in ['.//confidence', './/plateConfidence', f'.//{ns}confidence']:
            el = root.find(path)
            if el is not None and el.text:
                try:
                    conf = float(el.text)
                    result['confidence'] = conf / 100.0 if conf > 1 else conf
                except ValueError:
                    pass
                break

        # Cor do veiculo
        for path in ['.//vehicleColor', './/colorType', f'.//{ns}vehicleColor']:
            el = root.find(path)
            if el is not None and el.text:
                result['vehicle_color'] = el.text.strip()
                break

        # Tipo de veiculo
        for path in ['.//vehicleType', f'.//{ns}vehicleType']:
            el = root.find(path)
            if el is not None and el.text:
                vtype = el.text.strip().lower()
                type_map = {
                    'car': 'car', 'sedan': 'car', 'suv': 'car',
                    'motorcycle': 'motorcycle', 'bus': 'bus',
                    'truck': 'truck', 'van': 'van',
                }
                result['vehicle_type'] = type_map.get(vtype, 'unknown')
                break

        # Direcao
        for path in ['.//direction', './/plateDirection', f'.//{ns}direction']:
            el = root.find(path)
            if el is not None and el.text:
                result['direction'] = el.text.strip()
                break

        # Device ID / MAC
        for path in ['.//macAddress', './/deviceID', './/deviceName', f'.//{ns}macAddress']:
            el = root.find(path)
            if el is not None and el.text:
                result['device_id'] = el.text.strip()
                break

        # Timestamp
        for path in ['.//dateTime', './/captureTime', f'.//{ns}dateTime']:
            el = root.find(path)
            if el is not None and el.text:
                ts_text = el.text.strip()
                try:
                    result['timestamp'] = datetime.fromisoformat(ts_text.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    # Tentar formato Hikvision: 2026-03-22T21:37:58+08:00
                    try:
                        result['timestamp'] = datetime.strptime(ts_text[:19], '%Y-%m-%dT%H:%M:%S')
                        result['timestamp'] = timezone.make_aware(result['timestamp'])
                    except (ValueError, TypeError):
                        pass
                break

        # Imagem (base64 dentro do XML)
        for path in ['.//picture', './/plateImage', './/scenePicture', f'.//{ns}picture']:
            el = root.find(path)
            if el is not None and el.text:
                try:
                    result['image_data'] = base64.b64decode(el.text.strip())
                except Exception:
                    pass
                break

        logger.info(f"Hikvision ISAPI parsed: plate={result['plate_text']}, device={result['device_id']}")

    except Exception as e:
        logger.error(f"Erro ao parsear Hikvision XML: {e}")

    return result


# ============================================================
# Parser JSON generico (Intelbras JSON simples + outros)
# ============================================================

def parse_intelbras_push(data):
    """Parseia payload da Funcao Push Intelbras (formato JSON simples)."""
    result = {}

    plate = (
        data.get('PlateNumber') or
        data.get('plateNumber') or
        data.get('plate') or
        data.get('licensePlate') or
        data.get('placa') or
        ''
    )
    result['plate_text'] = plate.strip().upper()

    result['confidence'] = float(
        data.get('Confidence') or
        data.get('confidence') or
        data.get('confianca') or
        data.get('score') or
        0
    )
    if result['confidence'] > 1:
        result['confidence'] = result['confidence'] / 100.0

    result['vehicle_brand'] = (
        data.get('VehicleBrand') or data.get('vehicleBrand') or
        data.get('brand') or data.get('marca') or ''
    )
    result['vehicle_model'] = (
        data.get('VehicleModel') or data.get('vehicleModel') or
        data.get('model') or data.get('modelo') or ''
    )
    result['vehicle_color'] = (
        data.get('VehicleColor') or data.get('vehicleColor') or
        data.get('color') or data.get('cor') or ''
    )

    vtype = (
        data.get('VehicleType') or data.get('vehicleType') or
        data.get('type') or data.get('tipo') or 'unknown'
    )
    type_map = {
        'car': 'car', 'automovel': 'car', 'sedan': 'car', 'hatchback': 'car',
        'motorcycle': 'motorcycle', 'moto': 'motorcycle', 'motocicleta': 'motorcycle',
        'truck': 'truck', 'caminhao': 'truck',
        'bus': 'bus', 'onibus': 'bus',
        'van': 'van', 'furgao': 'van',
        'utilitario': 'utility', 'suv': 'utility',
    }
    result['vehicle_type'] = type_map.get(vtype.lower(), 'unknown')

    year = data.get('VehicleYear') or data.get('vehicleYear') or data.get('year') or data.get('ano')
    result['vehicle_year'] = int(year) if year else None

    result['city'] = data.get('City') or data.get('city') or data.get('cidade') or ''
    result['direction'] = data.get('Direction') or data.get('direction') or data.get('direcao') or ''
    result['trigger_source'] = data.get('TriggerSource') or data.get('triggerSource') or data.get('fonte') or ''
    result['device_id'] = (
        data.get('DeviceID') or data.get('deviceId') or
        data.get('device_id') or data.get('serialNumber') or ''
    )

    ts = data.get('DateTime') or data.get('dateTime') or data.get('timestamp') or data.get('data_hora')
    if ts:
        try:
            result['timestamp'] = datetime.fromisoformat(str(ts).replace('Z', '+00:00'))
        except (ValueError, TypeError):
            result['timestamp'] = timezone.now()
    else:
        result['timestamp'] = timezone.now()

    return result


# ============================================================
# Funcoes auxiliares async
# ============================================================

async def find_camera_async(request_data, camera_id=None, parsed_data=None):
    """Encontra a camera associada ao request (async)."""
    cam = None

    if camera_id:
        try:
            cam = await Camera.objects.aget(id=camera_id)
        except Camera.DoesNotExist:
            pass

    if not cam:
        device_id = ''
        if isinstance(request_data, dict):
            device_id = (
                request_data.get('DeviceID') or
                request_data.get('deviceId') or
                request_data.get('device_id') or
                request_data.get('serialNumber') or
                ''
            )
        if device_id:
            cam = await Camera.objects.filter(device_id=device_id).afirst()
            if not cam:
                cam = await Camera.objects.filter(stream_key=device_id).afirst()

    # Tentar pelo serial extraido do binario/XML (parsed_data)
    if not cam and parsed_data:
        serial = parsed_data.get('device_id', '')
        if serial:
            cam = await Camera.objects.filter(device_id=serial).afirst()
        device_ip = parsed_data.get('device_ip', '')
        if not cam and device_ip:
            cam = await Camera.objects.filter(stream_url__contains=device_ip).afirst()

    # Tentar por IP na stream_url
    if not cam and isinstance(request_data, dict):
        device_id = request_data.get('DeviceID') or request_data.get('deviceId') or ''
        if device_id:
            cam = await Camera.objects.filter(stream_url__contains=device_id).afirst()

    if not cam:
        cam = await Camera.objects.afirst()
        if cam:
            logger.warning(f"Camera nao identificada, usando fallback: {cam.name}")

    return cam


async def dedup_check(plate_text, cam_id, timestamp):
    """Verifica deduplicacao via cache + banco. Retorna True se duplicata."""
    if not plate_text:
        return False

    ts_str = timestamp.strftime('%Y%m%d%H%M%S') if timestamp else ''
    cache_key = f"lpr_dedup_{plate_text}_{cam_id}_{ts_str}"

    if await cache_get(cache_key):
        return True

    await cache_set(cache_key, True, 3600)

    if timestamp and await LPRDetection.objects.filter(
        camera_id=cam_id, plate_text=plate_text, timestamp=timestamp
    ).aexists():
        return True

    return False


async def save_detection_async(cam, parsed, trigger_source, plate_image_path="", full_frame_path=""):
    """Salva deteccao no banco com protecao contra duplicatas."""
    detection = LPRDetection(
        camera=cam,
        plate_text=parsed['plate_text'],
        confidence=parsed['confidence'],
        bbox=parsed.get('bbox', []),
        vehicle_brand=parsed.get('vehicle_brand', ''),
        vehicle_model=parsed.get('vehicle_model', ''),
        vehicle_color=parsed.get('vehicle_color', ''),
        vehicle_type=parsed.get('vehicle_type', 'unknown'),
        vehicle_year=parsed.get('vehicle_year'),
        city=parsed.get('city', ''),
        direction=parsed.get('direction', ''),
        trigger_source=trigger_source,
        device_id=parsed.get('device_id', ''),
        plate_image_path=plate_image_path,
        full_frame_path=full_frame_path,
        timestamp=parsed.get('timestamp') or timezone.now(),
    )
    try:
        await detection.asave()
        return detection
    except IntegrityError:
        return None


# ============================================================
# Detectar tipo de payload
# ============================================================

def detect_payload_type(request):
    """
    Detecta o tipo de payload recebido.
    Retorna: 'intelbras_json', 'intelbras_binary', 'hikvision_xml',
             'hikvision_multipart', 'json_generic', 'raw_binary', 'unknown'
    """
    content_type = (request.content_type or '').lower()
    data = request.data

    # XML -> Hikvision ISAPI
    if 'xml' in content_type:
        return 'hikvision_xml'

    # Raw bytes (pode ser Intelbras ou Hikvision)
    if isinstance(data, bytes):
        # Verificar se e XML
        if data.lstrip()[:5] in (b'<?xml', b'<Even', b'<ANPR', b'<even', b'<anpr'):
            return 'hikvision_xml'
        return 'raw_binary'

    # JSON dict
    if isinstance(data, dict):
        # KeepAlive Intelbras
        if data.get('Active') == 'keepAlive':
            return 'intelbras_keepalive'
        # Picture Intelbras V1.13
        if 'Picture' in data:
            return 'intelbras_binary'
        # Hikvision JSON (EventNotificationAlert)
        if 'EventNotificationAlert' in data or 'ANPR' in data:
            return 'hikvision_json'
        # TollgateInfo (Intelbras/Hikvision)
        if 'TollgateInfo' in data or 'tollgateInfo' in data:
            return 'intelbras_json'
        # JSON generico
        return 'json_generic'

    # Multipart
    if 'multipart' in content_type:
        # Hikvision ISAPI multipart inclui XML + imagem
        if hasattr(request, 'FILES') and request.FILES:
            return 'hikvision_multipart'
        return 'json_generic'

    return 'unknown'


# ============================================================
# Webhook principal
# ============================================================

@api_view(['POST', 'PUT', 'GET'])
@permission_classes([AllowAny])
@parser_classes(ALL_PARSERS)
async def webhook_push(request, camera_id=None):
    """
    Webhook async para receber push de cameras Intelbras/Hikvision.

    Aceita qualquer Content-Type e detecta automaticamente o formato.
    Suporta GET para health-check (cameras fazem GET antes de POST).

    POST /api/deteccoes/webhook/push/
    POST /api/deteccoes/webhook/push/<camera_id>/
    GET  /api/deteccoes/webhook/push/
    """
    # GET = health check (Hikvision e alguns modelos Intelbras verificam antes)
    if request.method == 'GET':
        return Response({
            'Result': True,
            'status': 'ok',
            'service': 'GTVision LPR Webhook',
        }, status=status.HTTP_200_OK)

    logger.info(
        f"Webhook push: camera_id={camera_id}, "
        f"content_type={request.content_type}, "
        f"method={request.method}, "
        f"data_type={type(request.data).__name__}, "
        f"content_length={request.META.get('CONTENT_LENGTH', 'unknown')}"
    )

    try:
        payload_type = detect_payload_type(request)
        logger.info(f"Payload detectado: {payload_type}")

        # === KeepAlive Intelbras ===
        if payload_type == 'intelbras_keepalive':
            data = request.data
            dev_id = data.get('DeviceID', '')
            logger.info(f"KeepAlive Intelbras: DeviceID={dev_id}")
            if dev_id:
                cam = await find_camera_async(data, camera_id)
                if cam:
                    await cache_set(f'intelbras_device_{dev_id}', cam.id, 3600)
                    await cache_set('intelbras_last_camera', cam.id, 3600)
            return Response({'Result': True, 'status': 'keepalive_ok'}, status=status.HTTP_200_OK)

        # === Hikvision XML (ISAPI) ===
        if payload_type == 'hikvision_xml':
            xml_data = request.data
            if isinstance(xml_data, dict):
                # DRF nao conseguiu parsear — tentar body raw
                xml_data = request.body

            parsed = parse_hikvision_xml(xml_data)

            # Verificar se e heartbeat/keepalive Hikvision
            if not parsed['plate_text']:
                is_heartbeat = False
                if isinstance(xml_data, bytes):
                    is_heartbeat = b'heartbeat' in xml_data.lower()
                elif isinstance(xml_data, str):
                    is_heartbeat = 'heartbeat' in xml_data.lower()
                if is_heartbeat:
                    logger.info("Hikvision heartbeat recebido")
                    return Response({'Result': True, 'status': 'heartbeat_ok'}, status=status.HTTP_200_OK)
                logger.info(f"Hikvision XML sem placa detectada")
                return Response({'Result': True, 'status': 'no_plate'}, status=status.HTTP_200_OK)

            cam = await find_camera_async({}, camera_id, parsed_data=parsed)
            if not cam:
                return Response({'Result': True, 'error': 'Nenhuma camera encontrada'}, status=status.HTTP_200_OK)

            if await dedup_check(parsed['plate_text'], cam.id, parsed.get('timestamp')):
                return Response({'Result': True, 'status': 'duplicate_ignored'}, status=status.HTTP_200_OK)

            full_frame_path = ""
            if parsed.get('image_data'):
                full_frame_path = await save_image_async(parsed['image_data'], prefix="hik_frame")

            detection = await save_detection_async(cam, parsed, 'hikvision_isapi', full_frame_path=full_frame_path)
            if not detection:
                return Response({'Result': True, 'status': 'duplicate_ignored'}, status=status.HTTP_200_OK)

            logger.info(
                f"Deteccao Hikvision: ID={detection.id} | "
                f"Placa={detection.plate_text} | Camera={cam.name}"
            )

            return Response({
                'Result': True,
                'success': True,
                'id': detection.id,
                'plate': detection.plate_text,
                'confidence': detection.confidence,
            }, status=status.HTTP_200_OK)

        # === Intelbras V1.13 Picture (dados no binario do JPEG) ===
        if payload_type == 'intelbras_binary':
            data = request.data
            content = None
            pic = data['Picture']
            if isinstance(pic, dict):
                normal = pic.get('NormalPic') or pic.get('normalPic') or {}
                content = normal.get('Content') or normal.get('content')

            if not content:
                logger.warning(f"Picture sem Content. Keys: {list(pic.keys()) if isinstance(pic, dict) else type(pic)}")
                return Response({'Result': True, 'status': 'picture_without_content'}, status=status.HTTP_200_OK)

            logger.info(f"Intelbras Picture: content_len={len(content)}")

            parsed = parse_intelbras_binary(content)
            logger.info(f"Intelbras decodificado: placa={parsed['plate_text']}, direction={parsed['direction']}")

            # Ignorar frames sem placa detectada
            if not parsed['plate_text']:
                logger.debug("Frame sem placa — descartado")
                return Response({'Result': True, 'status': 'no_plate'}, status=status.HTTP_200_OK)

            # Encontrar camera via cache ou fallback
            cam = None
            cached_cam_id = await cache_get('intelbras_last_camera')
            if cached_cam_id:
                try:
                    cam = await Camera.objects.aget(id=cached_cam_id)
                except Camera.DoesNotExist:
                    pass

            if not cam:
                cam = await find_camera_async(data, camera_id, parsed_data=parsed)
            if not cam:
                return Response({'Result': True, 'error': 'Nenhuma camera encontrada'}, status=status.HTTP_200_OK)

            if await dedup_check(parsed['plate_text'], cam.id, parsed.get('timestamp')):
                return Response({'Result': True, 'status': 'duplicate_ignored'}, status=status.HTTP_200_OK)

            full_frame_path = ""
            if parsed.get('image_data'):
                full_frame_path = await save_image_async(parsed['image_data'], prefix="frame")

            detection = await save_detection_async(cam, parsed, 'intelbras_v113', full_frame_path=full_frame_path)
            if not detection:
                return Response({'Result': True, 'status': 'duplicate_ignored'}, status=status.HTTP_200_OK)

            logger.info(
                f"Deteccao Intelbras: ID={detection.id} | "
                f"Placa={detection.plate_text} | Camera={cam.name}"
            )

            return Response({
                'Result': True,
                'success': True,
                'id': detection.id,
                'plate': detection.plate_text,
                'confidence': detection.confidence,
            }, status=status.HTTP_200_OK)

        # === Hikvision Multipart (XML + imagem em partes separadas) ===
        if payload_type == 'hikvision_multipart':
            parsed = None
            image_data = None

            # Procurar parte XML
            for key, f in request.FILES.items():
                content = f.read()
                f.seek(0)
                if content.lstrip()[:5] in (b'<?xml', b'<Even', b'<ANPR'):
                    parsed = parse_hikvision_xml(content)
                elif content[:2] == b'\xff\xd8':
                    image_data = content

            # Se nao encontrou no FILES, tentar no body
            if not parsed and isinstance(request.data, dict):
                parsed = parse_intelbras_push(request.data)
                parsed['trigger_source'] = 'hikvision_multipart'

            if not parsed or not parsed.get('plate_text'):
                return Response({'Result': True, 'status': 'no_plate'}, status=status.HTTP_200_OK)

            cam = await find_camera_async(request.data if isinstance(request.data, dict) else {}, camera_id, parsed_data=parsed)
            if not cam:
                return Response({'Result': True, 'error': 'Nenhuma camera encontrada'}, status=status.HTTP_200_OK)

            if await dedup_check(parsed['plate_text'], cam.id, parsed.get('timestamp')):
                return Response({'Result': True, 'status': 'duplicate_ignored'}, status=status.HTTP_200_OK)

            full_frame_path = ""
            if image_data:
                full_frame_path = await save_image_async(image_data, prefix="hik_frame")
            elif parsed.get('image_data'):
                full_frame_path = await save_image_async(parsed['image_data'], prefix="hik_frame")

            detection = await save_detection_async(cam, parsed, 'hikvision_multipart', full_frame_path=full_frame_path)
            if not detection:
                return Response({'Result': True, 'status': 'duplicate_ignored'}, status=status.HTTP_200_OK)

            return Response({
                'Result': True,
                'success': True,
                'id': detection.id,
                'plate': detection.plate_text,
            }, status=status.HTTP_200_OK)

        # === Raw binary (fallback — tentar Intelbras binario direto) ===
        if payload_type == 'raw_binary':
            raw_data = request.data
            if isinstance(raw_data, bytes):
                # Tentar decodificar como base64 ou direto
                try:
                    b64_content = raw_data.decode('utf-8', errors='ignore')
                    parsed = parse_intelbras_binary(b64_content)
                except Exception:
                    parsed = {'plate_text': '', 'confidence': 0.0, 'trigger_source': 'raw_binary'}

                if not parsed.get('plate_text'):
                    return Response({'Result': True, 'status': 'raw_no_plate'}, status=status.HTTP_200_OK)

                cam = await find_camera_async({}, camera_id, parsed_data=parsed)
                if not cam:
                    return Response({'Result': True, 'error': 'Nenhuma camera encontrada'}, status=status.HTTP_200_OK)

                full_frame_path = ""
                if parsed.get('image_data'):
                    full_frame_path = await save_image_async(parsed['image_data'], prefix="raw_frame")

                detection = await save_detection_async(cam, parsed, 'raw_binary', full_frame_path=full_frame_path)
                if detection:
                    return Response({
                        'Result': True,
                        'success': True,
                        'id': detection.id,
                        'plate': detection.plate_text,
                    }, status=status.HTTP_200_OK)

            return Response({'Result': True, 'status': 'raw_processed'}, status=status.HTTP_200_OK)

        # === JSON generico (formato simples, TollgateInfo, ou teste via curl) ===
        data = request.data
        if isinstance(data, dict):
            import json as _json
            try:
                raw_dump = _json.dumps(dict(data), default=str)[:3000]
                logger.info(f"Webhook JSON raw: {raw_dump}")
            except Exception:
                pass

            parsed = parse_intelbras_push(data)
            logger.info(f"Webhook JSON: placa={parsed['plate_text']}, confianca={parsed['confidence']}")

            if not parsed['plate_text']:
                logger.debug("JSON sem placa — descartado")
                return Response({'Result': True, 'status': 'no_plate'}, status=status.HTTP_200_OK)

            cam = await find_camera_async(data, camera_id)
            if not cam:
                return Response({'Result': True, 'error': 'Nenhuma camera encontrada'}, status=status.HTTP_200_OK)

            if await dedup_check(parsed['plate_text'], cam.id, parsed.get('timestamp')):
                return Response({'Result': True, 'status': 'duplicate_ignored'}, status=status.HTTP_200_OK)

            # Salvar imagens se enviadas via multipart
            plate_image_path = ""
            full_frame_path = ""

            for key in ['plate_image', 'plateImage', 'image']:
                if key in request.FILES:
                    plate_image_path = await save_image_async(request.FILES[key], prefix="plate")
                    break

            for key in ['full_image', 'fullImage', 'scene']:
                if key in request.FILES:
                    full_frame_path = await save_image_async(request.FILES[key], prefix="frame")
                    break

            detection = await save_detection_async(
                cam, parsed, parsed.get('trigger_source', ''),
                plate_image_path=plate_image_path, full_frame_path=full_frame_path,
            )
            if not detection:
                return Response({'Result': True, 'status': 'duplicate_ignored'}, status=status.HTTP_200_OK)

            logger.info(
                f"Deteccao push: ID={detection.id} | "
                f"Placa={detection.plate_text} | Camera={cam.name}"
            )

            return Response({
                'Result': True,
                'success': True,
                'id': detection.id,
                'plate': detection.plate_text,
                'confidence': detection.confidence,
            }, status=status.HTTP_200_OK)

        # Tipo desconhecido — logar e aceitar
        logger.warning(f"Payload tipo desconhecido: {payload_type}, data_type={type(request.data)}")
        return Response({'Result': True, 'status': 'unknown_format_accepted'}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Erro no webhook push: {str(e)}", exc_info=True)
        # SEMPRE retornar 200 para a camera nao parar de enviar
        return Response(
            {'Result': True, 'error': f'Erro interno: {str(e)}'},
            status=status.HTTP_200_OK
        )


# ============================================================
# Endpoints auxiliares
# ============================================================

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
async def webhook_test(request):
    """Endpoint de teste para verificar se o webhook esta acessivel."""
    return Response({
        'Result': True,
        'status': 'ok',
        'service': 'GTVision LPR Webhook (async)',
        'version': '3.0',
        'timestamp': timezone.now().isoformat(),
        'supported_formats': [
            'intelbras_v113_push',
            'hikvision_isapi_xml',
            'hikvision_multipart',
            'json_generic',
        ],
    })


@api_view(['POST', 'PUT', 'GET'])
@permission_classes([AllowAny])
@parser_classes(ALL_PARSERS)
async def webhook_hikvision(request, camera_id=None):
    """
    Endpoint dedicado Hikvision ISAPI.
    Redireciona para o webhook principal.

    POST /api/deteccoes/webhook/hikvision/
    POST /api/deteccoes/webhook/hikvision/<camera_id>/
    """
    return await webhook_push(request, camera_id=camera_id)
