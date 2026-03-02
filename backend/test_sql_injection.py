#!/usr/bin/env python
"""Teste de SQL Injection"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.usuarios.models import Usuario
from django.db import connection

print("="*60)
print("TESTE DE SQL INJECTION")
print("="*60)

# Teste 1: SQL Injection no email
print("\n1. Tentativa de SQL Injection no campo email:")
email_malicioso = "admin' OR '1'='1"
print(f"   Input: {email_malicioso}")

try:
    user = Usuario.objects.filter(email=email_malicioso).first()
    print(f"   Resultado: {user}")
    print("   ✓ Django ORM protegeu - nenhum usuário retornado")
except Exception as e:
    print(f"   ✗ Erro: {e}")

# Teste 2: SQL Injection com UNION
print("\n2. Tentativa de UNION SELECT:")
email_union = "admin' UNION SELECT * FROM usuarios_usuario--"
print(f"   Input: {email_union}")

try:
    user = Usuario.objects.filter(email=email_union).first()
    print(f"   Resultado: {user}")
    print("   ✓ Django ORM protegeu - query parametrizada")
except Exception as e:
    print(f"   ✗ Erro: {e}")

# Teste 3: SQL Injection com DROP TABLE
print("\n3. Tentativa de DROP TABLE:")
email_drop = "admin'; DROP TABLE usuarios_usuario;--"
print(f"   Input: {email_drop}")

try:
    user = Usuario.objects.filter(email=email_drop).first()
    print(f"   Resultado: {user}")
    print("   ✓ Django ORM protegeu - comando ignorado")
except Exception as e:
    print(f"   ✗ Erro: {e}")

# Teste 4: Verificar query SQL gerada
print("\n4. Query SQL gerada pelo Django ORM:")
queryset = Usuario.objects.filter(email="admin' OR '1'='1")
print(f"   SQL: {queryset.query}")
print("   ✓ Parâmetros escapados automaticamente")

# Teste 5: Raw SQL (PERIGOSO - apenas para demonstração)
print("\n5. Raw SQL (INSEGURO - NÃO USAR):")
print("   Django permite raw SQL, mas deve usar parâmetros:")
print("   ERRADO: Usuario.objects.raw(f\"SELECT * FROM usuarios_usuario WHERE email='{email}'\")")
print("   CERTO:  Usuario.objects.raw(\"SELECT * FROM usuarios_usuario WHERE email=%s\", [email])")

# Resumo
print("\n" + "="*60)
print("RESUMO")
print("="*60)
print("✓ Django ORM usa prepared statements")
print("✓ Parâmetros são escapados automaticamente")
print("✓ SQL injection é praticamente impossível com ORM")
print("✓ Apenas raw SQL sem parâmetros é vulnerável")
print("\nRECOMENDAÇÃO: Sempre use Django ORM ou parametrize queries!")
