"""
Settings para desenvolvimento - CSRF completamente desabilitado
"""
from .settings import *

# Desabilita CSRF completamente
MIDDLEWARE = [m for m in MIDDLEWARE if 'csrf' not in m.lower()]

# Remove validação CSRF
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

print("⚠️  MODO DESENVOLVIMENTO - CSRF DESABILITADO")
