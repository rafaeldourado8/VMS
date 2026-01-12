"""
Camera Type Detection Logic
RTSP → LPR IA ATIVA
RTMP → SEM IA (apenas gravação)
"""

def should_enable_lpr(camera_url: str) -> bool:
    """
    Determina se deve ativar LPR baseado no protocolo da câmera
    
    Args:
        camera_url: URL da câmera (rtsp:// ou rtmp://)
    
    Returns:
        True se deve processar LPR, False caso contrário
    """
    if not camera_url:
        return False
    
    url_lower = camera_url.lower()
    
    # RTSP = Alta definição = LPR ativo
    if url_lower.startswith('rtsp://'):
        return True
    
    # RTMP = Bullets = Apenas gravação
    if url_lower.startswith('rtmp://'):
        return False
    
    # Outros protocolos: não processar
    return False


def get_camera_type(camera_url: str) -> str:
    """
    Retorna o tipo de câmera baseado no protocolo
    
    Returns:
        'lpr' para RTSP, 'bullet' para RTMP, 'unknown' para outros
    """
    if not camera_url:
        return 'unknown'
    
    url_lower = camera_url.lower()
    
    if url_lower.startswith('rtsp://'):
        return 'lpr'
    elif url_lower.startswith('rtmp://'):
        return 'bullet'
    else:
        return 'unknown'


# Exemplo de uso no processamento
def process_recording(recording_path: str, camera_url: str):
    """
    Processa gravação baseado no tipo de câmera
    """
    camera_type = get_camera_type(camera_url)
    
    if camera_type == 'lpr':
        # Processa com YOLO + OCR
        print(f"🔍 Processando LPR: {recording_path}")
        # detector.process_video_file(recording_path)
    elif camera_type == 'bullet':
        # Apenas grava, não processa
        print(f"📹 Gravação bullet (sem LPR): {recording_path}")
    else:
        print(f"⚠️ Tipo de câmera desconhecido: {camera_url}")
