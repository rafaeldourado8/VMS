# Security App - Login Protection

from django.core.cache import cache
from django.conf import settings
from rest_framework.throttling import AnonRateThrottle
import re


class LoginRateThrottle(AnonRateThrottle):
    """Rate limiting para login: 5 tentativas por minuto"""
    rate = '5/min'


class LoginSecurityService:
    """Serviço de segurança para login"""
    
    LOCKOUT_DURATION = 300  # 5 minutos
    MAX_ATTEMPTS = 5
    
    @staticmethod
    def get_client_ip(request):
        """Obtém IP do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def is_locked_out(identifier):
        """Verifica se usuário/IP está bloqueado"""
        key = f'lockout:{identifier}'
        return cache.get(key, False)
    
    @staticmethod
    def record_failed_attempt(identifier):
        """Registra tentativa falha"""
        key = f'failed_attempts:{identifier}'
        attempts = cache.get(key, 0) + 1
        cache.set(key, attempts, 300)  # 5 minutos
        
        if attempts >= LoginSecurityService.MAX_ATTEMPTS:
            lockout_key = f'lockout:{identifier}'
            cache.set(lockout_key, True, LoginSecurityService.LOCKOUT_DURATION)
            return True, attempts
        
        return False, attempts
    
    @staticmethod
    def clear_failed_attempts(identifier):
        """Limpa tentativas após login bem-sucedido"""
        key = f'failed_attempts:{identifier}'
        cache.delete(key)
    
    @staticmethod
    def validate_password_strength(password):
        """Valida força da senha"""
        if len(password) < 8:
            return False, "Senha deve ter no mínimo 8 caracteres"
        
        if not re.search(r'[A-Z]', password):
            return False, "Senha deve conter pelo menos uma letra maiúscula"
        
        if not re.search(r'[a-z]', password):
            return False, "Senha deve conter pelo menos uma letra minúscula"
        
        if not re.search(r'\d', password):
            return False, "Senha deve conter pelo menos um número"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Senha deve conter pelo menos um caractere especial"
        
        return True, "Senha válida"
