import pytest
from admin.application import (
    CreateUserUseCase,
    UpdateUserPermissionsUseCase,
    CreateUserDTO
)


def test_update_user_permissions_success(user_repository):
    """Testa atualização de permissões com sucesso."""
    # Cria usuário
    create_use_case = CreateUserUseCase(user_repository)
    dto = CreateUserDTO(
        email="user@test.com",
        name="Test User",
        password="password123",
        city_ids=["city1"]
    )
    user = create_use_case.execute(dto)
    
    # Atualiza permissões
    update_use_case = UpdateUserPermissionsUseCase(user_repository)
    updated_user = update_use_case.execute(
        user_id=user.id,
        city_ids=["city1", "city2", "city3"],
        is_admin=False
    )
    
    assert updated_user.city_ids == ["city1", "city2", "city3"]
    assert updated_user.is_admin is False


def test_update_user_to_admin(user_repository):
    """Testa promoção de usuário para admin."""
    # Cria usuário
    create_use_case = CreateUserUseCase(user_repository)
    dto = CreateUserDTO(
        email="user@test.com",
        name="Test User",
        password="password123",
        city_ids=["city1"]
    )
    user = create_use_case.execute(dto)
    
    # Promove para admin
    update_use_case = UpdateUserPermissionsUseCase(user_repository)
    updated_user = update_use_case.execute(
        user_id=user.id,
        city_ids=[],
        is_admin=True
    )
    
    assert updated_user.is_admin is True


def test_update_user_not_found(user_repository):
    """Testa erro ao atualizar usuário inexistente."""
    update_use_case = UpdateUserPermissionsUseCase(user_repository)
    
    with pytest.raises(ValueError, match="não encontrado"):
        update_use_case.execute(
            user_id="invalid_id",
            city_ids=["city1"],
            is_admin=False
        )
