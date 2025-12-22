from apps.suporte.schemas import MensagemDTO

def test_mensagem_dto_structure():
    """Valida a estrutura da dataclass de mensagem."""
    dto = MensagemDTO(
        id=1,
        autor_id=10,
        autor_email="test@test.com",
        conteudo="Olá",
        timestamp=None,
        respondido_por_admin=False
    )
    assert dto.autor_email == "test@test.com"   