"""
URLs do admin com CSRF desabilitado para desenvolvimento
"""
from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

# Desabilita CSRF para todas as views do admin
admin.site.login = csrf_exempt(admin.site.login)
admin.site.logout = csrf_exempt(admin.site.logout)

urlpatterns = [
    path('admin/', admin.site.urls),
]
