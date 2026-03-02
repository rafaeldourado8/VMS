#!/usr/bin/env python
"""
Detector de Raw SQL Inseguro
Escaneia o código em busca de queries SQL vulneráveis
"""
import os
import re
from pathlib import Path

# Padrões perigosos
DANGEROUS_PATTERNS = [
    (r'\.raw\s*\(\s*f["\']', 'f-string em .raw() - SQL Injection!'),
    (r'\.raw\s*\(\s*["\'].*\{.*\}', 'String formatting em .raw() - SQL Injection!'),
    (r'\.raw\s*\(\s*.*\+.*["\']', 'Concatenação em .raw() - SQL Injection!'),
    (r'cursor\.execute\s*\(\s*f["\']', 'f-string em cursor.execute() - SQL Injection!'),
    (r'cursor\.execute\s*\(\s*["\'].*\{.*\}', 'String formatting em cursor.execute() - SQL Injection!'),
    (r'cursor\.execute\s*\(\s*.*\+.*["\']', 'Concatenação em cursor.execute() - SQL Injection!'),
]

# Padrões seguros (para referência)
SAFE_PATTERNS = [
    r'\.raw\s*\(\s*["\'][^"\']*["\'],\s*\[',  # .raw("SQL", [params])
    r'cursor\.execute\s*\(\s*["\'][^"\']*["\'],\s*\[',  # cursor.execute("SQL", [params])
]

def scan_file(filepath):
    """Escaneia um arquivo Python em busca de SQL inseguro"""
    vulnerabilities = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line_num, line in enumerate(lines, 1):
            for pattern, message in DANGEROUS_PATTERNS:
                if re.search(pattern, line):
                    vulnerabilities.append({
                        'file': filepath,
                        'line': line_num,
                        'code': line.strip(),
                        'message': message
                    })
    except Exception as e:
        pass
    
    return vulnerabilities

def scan_directory(directory):
    """Escaneia todos os arquivos Python em um diretório"""
    all_vulnerabilities = []
    
    for root, dirs, files in os.walk(directory):
        # Ignorar diretórios
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'migrations', 'venv', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                vulnerabilities = scan_file(filepath)
                all_vulnerabilities.extend(vulnerabilities)
    
    return all_vulnerabilities

if __name__ == '__main__':
    print("="*70)
    print("DETECTOR DE RAW SQL INSEGURO")
    print("="*70)
    
    # Escanear diretório apps
    base_dir = Path(__file__).parent
    apps_dir = base_dir / 'apps'
    
    print(f"\nEscaneando: {apps_dir}")
    vulnerabilities = scan_directory(apps_dir)
    
    if vulnerabilities:
        print(f"\n❌ ENCONTRADAS {len(vulnerabilities)} VULNERABILIDADES:\n")
        
        for vuln in vulnerabilities:
            print(f"Arquivo: {vuln['file']}")
            print(f"Linha {vuln['line']}: {vuln['code']}")
            print(f"⚠️  {vuln['message']}")
            print("-" * 70)
    else:
        print("\n✅ NENHUMA VULNERABILIDADE ENCONTRADA!")
        print("✅ Todo código usa ORM ou queries parametrizadas")
    
    print("\n" + "="*70)
    print("BOAS PRÁTICAS:")
    print("="*70)
    print("✅ SEGURO:")
    print("   Model.objects.filter(email=user_input)")
    print("   Model.objects.raw('SELECT * FROM table WHERE id=%s', [user_input])")
    print("   cursor.execute('SELECT * FROM table WHERE id=%s', [user_input])")
    print("\n❌ INSEGURO:")
    print("   Model.objects.raw(f'SELECT * FROM table WHERE id={user_input}')")
    print("   cursor.execute(f'SELECT * FROM table WHERE id={user_input}')")
    print("   cursor.execute('SELECT * FROM table WHERE id=' + user_input)")
