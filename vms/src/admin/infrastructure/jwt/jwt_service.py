import jwt
from datetime import datetime, timedelta
from typing import Optional


class JWTService:
    """Serviço JWT usando PyJWT."""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256", expires_in: int = 3600):
        self._secret = secret_key
        self._algorithm = algorithm
        self._expires_in = expires_in
    
    def generate_token(self, payload: dict) -> str:
        """Gera token JWT."""
        data = payload.copy()
        data["exp"] = datetime.utcnow() + timedelta(seconds=self._expires_in)
        data["iat"] = datetime.utcnow()
        return jwt.encode(data, self._secret, algorithm=self._algorithm)
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verifica e decodifica token."""
        try:
            return jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expirado")
        except jwt.InvalidTokenError:
            raise ValueError("Token inválido")
