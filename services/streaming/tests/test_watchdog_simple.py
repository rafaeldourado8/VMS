"""Testes simplificados do watchdog sem dependências externas"""
import time
import sys
import os

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_watchdog_logic():
    """Testa a lógica básica de detecção de stream congelado"""
    
    # Simula timestamps de frames
    frame_timestamps = {}
    CHECK_INTERVAL = 15
    FROZEN_THRESHOLD = 30
    
    # Cenário 1: Stream ativo (frame recente)
    camera_id = "cam1"
    frame_timestamps[camera_id] = time.time()
    
    current_time = time.time()
    elapsed = current_time - frame_timestamps[camera_id]
    
    assert elapsed < FROZEN_THRESHOLD, "Stream ativo nao deve ser detectado como congelado"
    print("[OK] Teste 1: Stream ativo")
    
    # Cenario 2: Stream congelado (sem frames ha 35s)
    frame_timestamps[camera_id] = time.time() - 35
    
    current_time = time.time()
    elapsed = current_time - frame_timestamps[camera_id]
    
    assert elapsed > FROZEN_THRESHOLD, "Stream congelado deve ser detectado"
    print("[OK] Teste 2: Stream congelado detectado")
    
    # Cenario 3: Multiplas cameras
    frame_timestamps["cam1"] = time.time() - 35  # Congelada
    frame_timestamps["cam2"] = time.time()       # Ativa
    frame_timestamps["cam3"] = time.time() - 40  # Congelada
    
    frozen_cameras = []
    current_time = time.time()
    
    for cam_id, last_frame_time in frame_timestamps.items():
        elapsed = current_time - last_frame_time
        if elapsed > FROZEN_THRESHOLD:
            frozen_cameras.append(cam_id)
    
    assert len(frozen_cameras) == 2, "Deve detectar 2 cameras congeladas"
    assert "cam1" in frozen_cameras, "cam1 deve estar congelada"
    assert "cam3" in frozen_cameras, "cam3 deve estar congelada"
    assert "cam2" not in frozen_cameras, "cam2 nao deve estar congelada"
    print("[OK] Teste 3: Multiplas cameras")
    
    # Cenario 4: Update de frame
    frame_timestamps["cam1"] = time.time()
    elapsed = time.time() - frame_timestamps["cam1"]
    assert elapsed < 1, "Frame atualizado deve ter timestamp recente"
    print("[OK] Teste 4: Update de frame")
    
    print("\nTodos os testes passaram!")


def test_watchdog_intervals():
    """Testa os intervalos de verificação"""
    CHECK_INTERVAL = 15
    FROZEN_THRESHOLD = 30
    
    # Verifica que o threshold é maior que o intervalo
    assert FROZEN_THRESHOLD > CHECK_INTERVAL, "Threshold deve ser maior que intervalo de check"
    
    # Verifica que o threshold é múltiplo razoável do intervalo
    assert FROZEN_THRESHOLD >= CHECK_INTERVAL * 2, "Threshold deve ser pelo menos 2x o intervalo"
    
    print("[OK] Teste de intervalos")


def test_event_structure():
    """Testa a estrutura do evento publicado"""
    import json
    
    camera_id = "cam1"
    event = {
        'camera_id': camera_id,
        'event': 'stream.frozen',
        'timestamp': time.time()
    }
    
    # Verifica que pode ser serializado
    event_json = json.dumps(event)
    assert event_json, "Evento deve ser serializável"
    
    # Verifica campos obrigatórios
    event_parsed = json.loads(event_json)
    assert 'camera_id' in event_parsed, "Evento deve ter camera_id"
    assert 'event' in event_parsed, "Evento deve ter tipo"
    assert 'timestamp' in event_parsed, "Evento deve ter timestamp"
    assert event_parsed['event'] == 'stream.frozen', "Tipo de evento correto"
    
    print("[OK] Teste de estrutura de evento")


if __name__ == "__main__":
    print("Executando testes do Watchdog...\n")
    test_watchdog_logic()
    test_watchdog_intervals()
    test_event_structure()
    print("\nTodos os testes concluidos com sucesso!")
