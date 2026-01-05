import pytest
from unittest.mock import Mock
from datetime import datetime
from application.detection.commands.process_detection_command import ProcessDetectionCommand
from application.detection.handlers.process_detection_handler import ProcessDetectionHandler
from domain.detection.entities.detection import Detection


def test_process_detection_success():
    mock_repo = Mock()
    mock_repo.save.return_value = Detection(
        id=1,
        camera_id=100,
        plate=Mock(),
        confidence=Mock(),
        timestamp=datetime.now()
    )
    
    handler = ProcessDetectionHandler(mock_repo)
    command = ProcessDetectionCommand(
        camera_id=100,
        plate="ABC1234",
        confidence=0.95,
        timestamp=datetime.now(),
        vehicle_type="car"
    )
    
    result = handler.handle(command)
    
    assert result.id == 1
    assert result.camera_id == 100
    mock_repo.save.assert_called_once()


def test_process_detection_with_none_plate():
    mock_repo = Mock()
    mock_repo.save.return_value = Detection(
        id=1,
        camera_id=100,
        plate=Mock(),
        confidence=Mock(),
        timestamp=datetime.now()
    )
    
    handler = ProcessDetectionHandler(mock_repo)
    command = ProcessDetectionCommand(
        camera_id=100,
        plate=None,
        confidence=0.75,
        timestamp=datetime.now()
    )
    
    result = handler.handle(command)
    
    mock_repo.save.assert_called_once()
