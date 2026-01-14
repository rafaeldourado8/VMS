from fastapi import Request, HTTPException


def get_current_user(request: Request) -> str:
    """Retorna user_id do token JWT."""
    if not hasattr(request.state, "user_id"):
        raise HTTPException(401, "Não autenticado")
    return request.state.user_id


def require_admin(request: Request):
    """Valida se usuário é admin."""
    if not hasattr(request.state, "is_admin") or not request.state.is_admin:
        raise HTTPException(403, "Acesso negado")
