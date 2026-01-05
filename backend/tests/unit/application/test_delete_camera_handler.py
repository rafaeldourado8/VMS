import pytest
from unittest.mock import Mock
from application.monitoring.commands.delete_camera_command import DeleteCameraCommand
from application.monitoring.handlers.delete_camera_handler import DeleteCameraHandler
from domain.monitoring.entities.camera import Camera
from domain.monitoring.exceptions import CameraNotFoundException


def test_delete_camera_success():
    mock_repo = Mock()
    mock_repo.find_by_id.return_value = Camera(
        id=1,
        owner_id=100,
        name="Test",
        stream_url=Mock()
    )
    
    handler = DeleteCameraHandler(mock_repo)
    command = DeleteCameraCommand(camera_id=1, owner_id=100)
    
    handler.handle(command)
    
    mock_repo.delete.assert_called_once_with(1)


def test_delete_camera_not_found_raises_error():
    mock_repo = Mock()
    mock_repo.find_by_id.return_value = None
    
    handler = DeleteCameraHandler(mock_repo)
    command = DeleteCameraCommand(camera_id=999, owner_id=100)
    
    with pytest.raises(CameraNotFoundException):
        handler.handle(command)


def test_delete_camera_wrong_owner_raises_error():
    mock_repo = Mock()
    mock_repo.find_by_id.return_value = Camera(
        id=1,
        owner_id=100,
        name="Test",
        stream_url=Mock()
    )
    
    handler = DeleteCameraHandler(mock_repo)
    command = DeleteCameraCommand(camera_id=1, owner_id=999)
    
    with pytest.raises(PermissionError):
        handler.handle(command)
