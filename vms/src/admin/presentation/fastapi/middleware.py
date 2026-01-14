from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from .container import container


class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Rotas públicas
        public_paths = [
            "/api/auth/login",
            "/api/auth/register",
            "/health",
            "/docs",
            "/openapi.json"
        ]
        
        if request.url.path in public_paths:
            return await call_next(request)
        
        # Verifica token
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(401, "Token não fornecido")
        
        token = auth_header.replace("Bearer ", "")
        
        try:
            jwt_service = container.get_jwt_service()
            payload = jwt_service.verify_token(token)
            request.state.user_id = payload["user_id"]
            request.state.is_admin = payload.get("is_admin", False)
        except ValueError as e:
            raise HTTPException(401, str(e))
        
        return await call_next(request)
