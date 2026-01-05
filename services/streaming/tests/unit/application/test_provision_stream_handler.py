import pytest
from unittest.mock import Mock
from application.streaming.commands.provision_stream_command import ProvisionStreamCommand
from application.streaming.handlers.provision_stream_handler import ProvisionStreamHandler
from domain.streaming.exceptions import StreamAlreadyExistsException


def test_provision_stream_success():
    mock_repo = Mock()
    mock_repo.exists.return_value = False
    mock_repo.save.return_value = Mock(camera_id=1)
    
    handler = ProvisionStreamHandler(mock_repo)
    command = ProvisionStreamCommand(
        camera_id=1,
        rtsp_url="rtsp://test.com",
        name="Test Camera"
    )
    
    result = handler.handle(command)
    
    assert result.camera_id == 1
    mock_repo.save.assert_called_once()


def test_provision_stream_already_exists():
    mock_repo = Mock()
    mock_repo.exists.return_value = True
    
    handler = ProvisionStreamHandler(mock_repo)
    command = ProvisionStreamCommand(
        camera_id=1,
        rtsp_url="rtsp://test.com",
        name="Test"
    )
    
    with pytest.raises(StreamAlreadyExistsException):
        handler.handle(command)


def test_provision_stream_with_custom_base_url():
    mock_repo = Mock()
    mock_repo.exists.return_value = False
    mock_repo.save.return_value = Mock(camera_id=1)
    
    handler = ProvisionStreamHandler(mock_repo, base_url="http://custom:8889")
    command = ProvisionStreamCommand(
        camera_id=1,
        rtsp_url="rtsp://test.com",
        name="Test"
    )
    
    result = handler.handle(command)
    
    mock_repo.save.assert_called_once()
