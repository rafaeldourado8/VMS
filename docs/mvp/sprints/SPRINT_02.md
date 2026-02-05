# 🎯 SPRINT 2: RETENÇÃO CÍCLICA (7 DIAS)

**Duração**: 1 semana  
**Objetivo**: Validar que arquivos antigos são apagados automaticamente após 7 dias

---

## TAREFAS

### 2.1 Criar Arquivos de Teste (Simular 10 dias)
```bash
# Script para criar estrutura de 10 dias
for day in {0..10}; do
  date_str=$(date -d "$day days ago" +%Y-%m-%d)
  mkdir -p /recordings/cam_999/$date_str
  
  for hour in {00..23}; do
    # Criar arquivo vazio de 1GB (simula gravação)
    dd if=/dev/zero of=/recordings/cam_999/$date_str/$hour.mp4 bs=1M count=1000
    
    # Ajustar timestamp do arquivo
    touch -d "$date_str $hour:00:00" /recordings/cam_999/$date_str/$hour.mp4
  done
done
```

### 2.2 Monitorar Deleção Automática
```bash
# Verificar idade dos arquivos
find /recordings/cam_999 -name "*.mp4" -mtime +7 -ls

# Monitorar logs do MediaMTX
docker logs -f gtvision_mediamtx | grep "delete"
```

### 2.3 Validar Espaço em Disco
```bash
# Antes da deleção
du -sh /recordings/cam_999/

# Após 7 dias
du -sh /recordings/cam_999/

# Deve ter ~7 dias de gravação (não 10)
```

---

## CRITÉRIOS DE ACEITAÇÃO

- [ ] Arquivos com mais de 168h são apagados automaticamente
- [ ] Deleção ocorre sem intervenção manual
- [ ] Gravação continua normalmente durante deleção
- [ ] Espaço em disco estabiliza em ~7 dias
- [ ] Logs confirmam deleção

---

## TESTES

### Teste 1: Deleção Automática
```bash
# Criar arquivo de 8 dias atrás
date_old=$(date -d "8 days ago" +%Y-%m-%d)
mkdir -p /recordings/cam_999/$date_old
dd if=/dev/zero of=/recordings/cam_999/$date_old/00.mp4 bs=1M count=1000

# Aguardar 1 hora
sleep 3600

# Verificar se foi apagado
ls /recordings/cam_999/$date_old/
# Deve retornar: No such file or directory
```

### Teste 2: Deleção Gradual
```bash
# Monitorar deleção hora a hora
watch -n 3600 'find /recordings/cam_999 -name "*.mp4" | wc -l'

# Deve estabilizar em 168 arquivos (7 dias × 24 horas)
```

---

## PROBLEMAS ESPERADOS

### Problema 1: Arquivos não são apagados
**Sintoma**: Disco cheio, arquivos > 7 dias existem

**Debug**:
```bash
# Verificar configuração
grep recordDeleteAfter mediamtx.yml

# Verificar permissões
ls -la /recordings/cam_999/
```

**Solução**: Verificar `recordDeleteAfter: 168h`

### Problema 2: Deleção muito agressiva
**Sintoma**: Arquivos de 6 dias são apagados

**Debug**:
```bash
# Verificar timestamp dos arquivos
stat /recordings/cam_999/*/00.mp4
```

**Solução**: Verificar timezone do container

---

## ENTREGÁVEIS

- [ ] Script de teste de retenção
- [ ] Relatório de deleção automática
- [ ] Gráfico de uso de disco ao longo do tempo
- [ ] Documentação de comportamento
