# 🐛 Sessão Não Expira com Usuário Inativo

## Resumo
Usuários permanecem logados indefinidamente mesmo após longos períodos de inatividade, consumindo recursos desnecessários.

## Severidade
- [x] Alta (funcionalidade importante afetada)

## Componente Afetado
- Serviço: Backend (Django)
- Arquivo: `backend/config/settings.py`
- Função/Componente: Session Management

## Ambiente
- OS: Linux (Docker)
- Docker: 24.0.7
- Django: 4.2
- Redis: 7.2

## Descrição Detalhada

O sistema não está configurado para expirar sessões de usuários inativos. Isso causa:
1. Sessões acumuladas no Redis
2. Memória desperdiçada
3. Usuários "fantasma" contados como ativos
4. Possível risco de segurança (sessões abandonadas)

## Como Reproduzir

1. Fazer login no sistema
2. Deixar navegador aberto sem interação
3. Aguardar 4+ minutos
4. Verificar que ainda está logado
5. Verificar Redis: `docker-compose exec redis_cache redis-cli KEYS "session:*"`
6. Observar sessões antigas ainda presentes

## Comportamento Esperado

- Após 4 minutos de inatividade, usuário deve ser deslogado automaticamente
- Sessão deve ser removida do Redis
- Próxima requisição deve retornar 401 Unauthorized

## Comportamento Atual

- Usuário permanece logado indefinidamente
- Sessão nunca expira
- Redis acumula sessões antigas

## Screenshots/Logs

```bash
# Redis mostrando sessões antigas
127.0.0.1:6379> KEYS "session:*"
1) "session:abc123" # 2 horas atrás
2) "session:def456" # 5 horas atrás
3) "session:ghi789" # 1 dia atrás
```

## Impacto

- Usuários afetados: 100% (todos)
- Frequência: Sempre
- Workaround disponível: Não (logout manual)

### Impacto em Recursos

**Memória Redis:**
```
Sessões ativas: 100 usuários
Sessões abandonadas: 500+ (acumuladas)
Memória por sessão: ~5KB
Desperdício: 500 × 5KB = 2.5MB

Com 1000 usuários/dia:
Desperdício mensal: 1000 × 30 × 5KB = 150MB
```

**Custo:**
```
Redis memory: 150MB extra
Custo: $0.023/GB/mês
Desperdício: 0.15GB × $0.023 = $0.003/mês

Parece pouco, mas:
- Escala com usuários
- Afeta performance
- Risco de segurança
```
