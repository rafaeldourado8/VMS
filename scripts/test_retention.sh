#!/bin/bash
# Script para testar retenção cíclica de 7 dias

echo "🧪 Teste de Retenção Cíclica - MediaMTX"
echo "========================================"

# Criar arquivos de teste de 8 dias atrás
for day in 8 9 10; do
  date_str=$(date -d "$day days ago" +%Y-%m-%d 2>/dev/null || date -v-${day}d +%Y-%m-%d)
  
  echo "📁 Criando arquivos para $date_str (${day} dias atrás)..."
  
  mkdir -p /recordings/cam_test/$date_str
  
  # Criar 3 arquivos de teste
  for hour in 00 12 23; do
    file="/recordings/cam_test/$date_str/$hour-00-00-000001.mp4"
    
    # Criar arquivo de 10MB
    dd if=/dev/zero of="$file" bs=1M count=10 2>/dev/null
    
    # Ajustar timestamp para simular arquivo antigo
    touch -d "$date_str $hour:00:00" "$file"
    
    echo "  ✅ $file ($(stat -c%s "$file" | numfmt --to=iec-i))"
  done
done

echo ""
echo "📊 Resumo:"
echo "  Total de arquivos criados: $(find /recordings/cam_test -name '*.mp4' | wc -l)"
echo "  Espaço usado: $(du -sh /recordings/cam_test | cut -f1)"
echo ""
echo "⏳ Aguardando MediaMTX detectar e deletar arquivos > 7 dias..."
echo "   (Verificar logs: docker logs -f gtvision_mediamtx | grep delete)"
