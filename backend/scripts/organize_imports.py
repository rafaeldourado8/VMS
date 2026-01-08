"""
Script para organizar imports em todos os arquivos Python
"""

import os
import re
from pathlib import Path

def organize_imports_in_file(file_path):
    """Organiza imports em um arquivo específico"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Separar imports
    stdlib_imports = []
    third_party_imports = []
    local_imports = []
    other_lines = []
    
    in_imports = True
    
    for line in lines:
        stripped = line.strip()
        
        if not stripped or stripped.startswith('#'):
            if in_imports:
                continue
            other_lines.append(line)
            continue
            
        if stripped.startswith('from ') or stripped.startswith('import '):
            if in_imports:
                if any(lib in stripped for lib in ['django', 'rest_framework', 'celery']):
                    third_party_imports.append(line)
                elif any(lib in stripped for lib in ['domain', 'application', 'infrastructure', 'apps']):
                    local_imports.append(line)
                else:
                    stdlib_imports.append(line)
            else:
                other_lines.append(line)
        else:
            in_imports = False
            other_lines.append(line)
    
    # Reorganizar
    organized = []
    
    if stdlib_imports:
        organized.extend(sorted(stdlib_imports))
        organized.append('')
    
    if third_party_imports:
        organized.extend(sorted(third_party_imports))
        organized.append('')
    
    if local_imports:
        organized.extend(sorted(local_imports))
        organized.append('')
    
    organized.extend(other_lines)
    
    # Remover linhas vazias excessivas
    final_content = '\n'.join(organized)
    final_content = re.sub(r'\n{3,}', '\n\n', final_content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_content)

def organize_all_imports():
    """Organiza imports em todos os arquivos Python"""
    
    directories = ['domain', 'application', 'infrastructure', 'apps']
    
    for directory in directories:
        if not os.path.exists(directory):
            continue
            
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    file_path = os.path.join(root, file)
                    try:
                        organize_imports_in_file(file_path)
                        print(f"OK Organizado: {file_path}")
                    except Exception as e:
                        print(f"ERRO em {file_path}: {e}")

if __name__ == "__main__":
    organize_all_imports()
    print("Organização de imports concluída")