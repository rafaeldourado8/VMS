from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache


def health_check(request):
    """Endpoint de health check para monitoramento"""
    
    status = {
        "status": "healthy",
        "database": "unknown",
        "cache": "unknown"
    }
    
    # Testar conexão com banco
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        status["database"] = "connected"
    except Exception as e:
        status["database"] = f"error: {str(e)}"
        status["status"] = "unhealthy"
    
    # Testar conexão com cache
    try:
        cache.set("health_check", "ok", 10)
        if cache.get("health_check") == "ok":
            status["cache"] = "connected"
        else:
            status["cache"] = "error"
    except Exception as e:
        status["cache"] = f"error: {str(e)}"
    
    return JsonResponse(status)