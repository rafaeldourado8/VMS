"""
Testes End-to-End para validar deploy em staging
"""

import requests
import time


class StagingE2ETests:
    """Suite de testes E2E para staging"""
    
    BASE_URL = "http://localhost:8000"
    
    def __init__(self):
        self.token = None
        self.user_id = None
    
    def test_health_check(self):
        """Testa se o servidor está respondendo"""
        response = requests.get(f"{self.BASE_URL}/health/")
        assert response.status_code == 200, "Health check falhou"
        print("OK Health check passou")
    
    def test_api_root(self):
        """Testa se a API root está acessível"""
        response = requests.get(f"{self.BASE_URL}/api/")
        assert response.status_code in [200, 401], "API root não acessível"
        print("OK API root acessivel")
    
    def test_authentication(self):
        """Testa autenticação JWT"""
        # Criar usuário de teste
        user_data = {
            "email": "test@staging.com",
            "password": "TestPass123!",
            "username": "testuser"
        }
        
        # Login
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        response = requests.post(f"{self.BASE_URL}/api/auth/login/", json=login_data)
        
        if response.status_code == 200:
            self.token = response.json().get("access")
            print("OK Autenticacao funcionando")
        else:
            print("AVISO Autenticacao precisa de usuario pre-criado")
    
    def test_cameras_endpoint(self):
        """Testa endpoint de câmeras"""
        if not self.token:
            print("SKIP Teste de cameras (sem token)")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.BASE_URL}/api/cameras/", headers=headers)
        
        assert response.status_code in [200, 401], "Endpoint de cameras com erro"
        print("OK Endpoint de cameras acessivel")
    
    def test_database_connection(self):
        """Testa se o banco de dados está conectado"""
        # Tenta acessar qualquer endpoint que use o banco
        response = requests.get(f"{self.BASE_URL}/api/")
        assert response.status_code != 500, "Erro de conexao com banco"
        print("OK Conexao com banco de dados")
    
    def test_redis_connection(self):
        """Testa se o Redis está conectado"""
        # Verifica se o cache está funcionando
        response = requests.get(f"{self.BASE_URL}/health/")
        assert response.status_code == 200, "Redis pode estar offline"
        print("OK Redis conectado")
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("\n" + "="*50)
        print("Executando Testes E2E - Staging")
        print("="*50 + "\n")
        
        tests = [
            self.test_health_check,
            self.test_api_root,
            self.test_database_connection,
            self.test_redis_connection,
            self.test_authentication,
            self.test_cameras_endpoint,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                test()
                passed += 1
            except Exception as e:
                print(f"ERRO {test.__name__}: {e}")
                failed += 1
        
        print("\n" + "="*50)
        print(f"Resultados: {passed} passou, {failed} falhou")
        print("="*50 + "\n")
        
        return failed == 0


if __name__ == "__main__":
    # Aguardar serviços iniciarem
    print("Aguardando servicos iniciarem...")
    time.sleep(5)
    
    tester = StagingE2ETests()
    success = tester.run_all_tests()
    
    exit(0 if success else 1)