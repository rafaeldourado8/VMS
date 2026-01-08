"""
Teste básico para validar implementação da Fase 6
"""

def test_support_message_creation():
    """Testa criação de mensagem de suporte"""
    from domain.support.entities.support_message import SupportMessage
    from datetime import datetime
    
    message = SupportMessage(
        id=None,
        author_id=1,
        content="Teste de mensagem",
        timestamp=datetime.now(),
        is_admin_response=False
    )
    
    assert message.content == "Teste de mensagem"
    assert not message.is_from_admin()
    print("OK SupportMessage criada com sucesso")


def test_clip_creation():
    """Testa criação de clip"""
    from domain.clips.entities.clip import Clip
    from datetime import datetime, timedelta
    
    now = datetime.now()
    clip = Clip(
        id=None,
        owner_id=1,
        camera_id=1,
        name="Teste Clip",
        start_time=now,
        end_time=now + timedelta(minutes=5),
        file_path="/path/to/clip.mp4",
        thumbnail_path="/path/to/thumb.jpg",
        duration_seconds=300,
        created_at=now
    )
    
    assert clip.name == "Teste Clip"
    assert clip.get_duration_minutes() == 5.0
    print("OK Clip criado com sucesso")


if __name__ == "__main__":
    test_support_message_creation()
    test_clip_creation()
    print("TODOS OS TESTES PASSARAM!")