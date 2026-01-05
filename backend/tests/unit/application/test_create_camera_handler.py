import pytest
from unittest.mock import Mock
from application.monitoring.commands.create_camera_command import CreateCameraCommand
from application.monitoring.handlers.create_camera_handler import CreateCameraHandler
from domain.monitoring.entities.camera import Camera


def test_create_camera_success():
    mock_repo = Mock()
    mock_repo.exists_by_name.return_value = False
    mock_repo.save.return_value = Camera(
        id=1,
        owner_id=100,
        name="Test Camera",
        stream_url=Mock()
    )
    
    handler = CreateCameraHandler(mock_repo)
    command = CreateCameraCommand(
        owner_id=100,
        name="Test Camera",
        stream_url="rtsp://test.com"
    )
    
    result = handler.handle(command)
    
    assert result.id == 1
    assert result.name == "Test Camera"
    mock_repo.save.assert_called_once()


def test_create_camera_duplicate_name_raises_error():
    mock_repo = Mock()
    mock_repo.exists_by_name.return_value = True
    
    handler = CreateCameraHandler(mock_repo)
    command = CreateCameraCommand(
        owner_id=100,
        name="Duplicate",
        stream_url="rtsp://test.com"
    )
    
    with pytest.raises(ValueError, match="já existe"):
        handler.handle(command)
