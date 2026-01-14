def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_user(client):
    response = client.post("/api/auth/register", json={
        "email": "new@example.com",
        "name": "New User",
        "password": "senha123",
        "city_ids": ["sao-paulo"]
    })
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == "new@example.com"
    assert data["name"] == "New User"
    assert data["is_active"] is True


def test_register_duplicate_email(client):
    # Primeiro registro
    client.post("/api/auth/register", json={
        "email": "dup@example.com",
        "name": "User 1",
        "password": "senha123"
    })
    
    # Segundo registro com mesmo email
    response = client.post("/api/auth/register", json={
        "email": "dup@example.com",
        "name": "User 2",
        "password": "senha456"
    })
    assert response.status_code == 400


def test_login_success(client):
    # Registra usuário
    client.post("/api/auth/register", json={
        "email": "login@example.com",
        "name": "Login User",
        "password": "senha123"
    })
    
    # Login
    response = client.post("/api/auth/login", json={
        "email": "login@example.com",
        "password": "senha123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "user" in data
    assert data["user"]["email"] == "login@example.com"


def test_login_invalid_email(client):
    response = client.post("/api/auth/login", json={
        "email": "notfound@example.com",
        "password": "senha123"
    })
    assert response.status_code == 401


def test_login_invalid_password(client):
    # Registra usuário
    client.post("/api/auth/register", json={
        "email": "wrong@example.com",
        "name": "Wrong User",
        "password": "senha123"
    })
    
    # Login com senha errada
    response = client.post("/api/auth/login", json={
        "email": "wrong@example.com",
        "password": "senhaerrada"
    })
    assert response.status_code == 401


def test_get_me_success(client, auth_token):
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"


def test_get_me_unauthorized(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_get_me_invalid_token(client):
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_update_permissions_admin(client):
    # Cria admin
    client.post("/api/auth/register", json={
        "email": "admin@example.com",
        "name": "Admin User",
        "password": "senha123",
        "is_admin": True
    })
    
    # Login admin
    response = client.post("/api/auth/login", json={
        "email": "admin@example.com",
        "password": "senha123"
    })
    admin_token = response.json()["token"]
    
    # Cria usuário normal
    response = client.post("/api/auth/register", json={
        "email": "normal@example.com",
        "name": "Normal User",
        "password": "senha123"
    })
    user_id = response.json()["id"]
    
    # Admin atualiza permissões
    response = client.put(
        f"/api/auth/permissions/{user_id}",
        json=["rio-de-janeiro", "belo-horizonte"],
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "rio-de-janeiro" in data["city_ids"]
    assert "belo-horizonte" in data["city_ids"]


def test_update_permissions_non_admin(client, auth_token):
    response = client.put(
        "/api/auth/permissions/some-user-id",
        json=["rio-de-janeiro"],
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 403
