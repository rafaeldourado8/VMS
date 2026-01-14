from admin.domain import Permission


def test_permission_values():
    """Testa valores das permissões."""
    assert Permission.VIEW_CAMERAS.value == "view_cameras"
    assert Permission.MANAGE_CAMERAS.value == "manage_cameras"
    assert Permission.VIEW_DETECTIONS.value == "view_detections"
    assert Permission.MANAGE_BLACKLIST.value == "manage_blacklist"
    assert Permission.VIEW_RECORDINGS.value == "view_recordings"
    assert Permission.CREATE_CLIPS.value == "create_clips"
    assert Permission.ADMIN_ALL.value == "admin_all"


def test_permission_str():
    """Testa conversão para string."""
    assert str(Permission.VIEW_CAMERAS) == "view_cameras"
    assert str(Permission.ADMIN_ALL) == "admin_all"
