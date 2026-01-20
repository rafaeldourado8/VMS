import pytest
import numpy as np
import cv2
from core.motion_detector import MotionDetector
from core.quality_scorer import QualityScorer
from pipeline.consensus_engine import ConsensusEngine

def test_motion_detector():
    detector = MotionDetector(threshold=0.03)
    
    # Frame estático
    frame1 = np.zeros((480, 640, 3), dtype=np.uint8)
    has_motion, ratio = detector.detect(frame1)
    
    # Primeiro frame sempre tem movimento (background learning)
    assert ratio >= 0
    
    # Frame com movimento
    frame2 = frame1.copy()
    cv2.rectangle(frame2, (100, 100), (200, 200), (255, 255, 255), -1)
    has_motion, ratio = detector.detect(frame2)
    
    assert ratio > 0

def test_quality_scorer():
    scorer = QualityScorer()
    
    # Frame de teste
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    bbox = (100, 100, 300, 300)
    
    result = scorer.score(frame, bbox)
    
    assert 'final' in result
    assert 'blur' in result
    assert 'angle' in result
    assert 'contrast' in result
    assert 'size' in result
    assert 0 <= result['final'] <= 100

def test_consensus_engine_simple_majority():
    engine = ConsensusEngine(min_readings=3)
    
    readings = [
        {'plate': 'ABC1234', 'confidence': 0.85},
        {'plate': 'ABC1234', 'confidence': 0.90},
        {'plate': 'ABC1234', 'confidence': 0.88},
        {'plate': 'XYZ5678', 'confidence': 0.75}
    ]
    
    result = engine.vote(readings)
    
    assert result is not None
    assert result['plate'] == 'ABC1234'
    assert result['method'] == 'simple_majority'
    assert result['votes'] == 3

def test_consensus_engine_similarity():
    engine = ConsensusEngine(min_readings=3)
    
    readings = [
        {'plate': 'ABC1234', 'confidence': 0.85},
        {'plate': 'ABC1Z34', 'confidence': 0.80},  # Similar
        {'plate': 'ABC1234', 'confidence': 0.90}
    ]
    
    result = engine.vote(readings)
    
    assert result is not None
    assert result['plate'] in ['ABC1234', 'ABC1Z34']
    assert result['method'] in ['simple_majority', 'similarity_voting']

def test_consensus_engine_no_consensus():
    engine = ConsensusEngine(min_readings=3)
    
    readings = [
        {'plate': 'ABC1234', 'confidence': 0.85},
        {'plate': 'XYZ5678', 'confidence': 0.90},
        {'plate': 'DEF9012', 'confidence': 0.88}
    ]
    
    result = engine.vote(readings)
    
    assert result is not None
    assert result['method'] == 'highest_confidence'
    assert result['plate'] == 'XYZ5678'  # Maior confidence

def test_consensus_engine_insufficient_readings():
    engine = ConsensusEngine(min_readings=3)
    
    readings = [
        {'plate': 'ABC1234', 'confidence': 0.85}
    ]
    
    result = engine.vote(readings)
    
    assert result is None

if __name__ == "__main__":
    pytest.main([__file__, '-v'])
