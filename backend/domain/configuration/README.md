# Configuration Context

## Visão Geral

O contexto de configurações gerencia as configurações globais do sistema VMS usando arquitetura DDD.

## Funcionalidades

### Configurações Disponíveis

- **Notificações**: Habilitar/desabilitar notificações do sistema
- **Email de Suporte**: Email para contato de suporte técnico
- **Modo de Manutenção**: Ativar/desativar modo de manutenção

### Regras de Negócio

1. **Singleton**: Existe apenas uma configuração global no sistema
2. **Email Válido**: Email de suporte deve ter formato válido
3. **Sistema Disponível**: Sistema indisponível quando em modo de manutenção

## API Endpoints

### GET /api/configuracoes/
Retorna configuração global atual.

**Resposta:**
```json
{
  "notifications_enabled": true,
  "support_email": "suporte@vms.com",
  "maintenance_mode": false,
  "system_available": true
}
```

### PATCH /api/configuracoes/
Atualiza configuração global.

**Payload:**
```json
{
  "notificacoes_habilitadas": false,
  "email_suporte": "novo@suporte.com",
  "em_manutencao": true
}
```

## Arquitetura

### Domain Layer
- `Configuration` - Entidade principal
- `SupportEmail` - Value object para email
- `ConfigurationRepository` - Interface de repositório

### Application Layer
- `GetConfigurationQuery/Handler` - Buscar configuração
- `UpdateConfigurationCommand/Handler` - Atualizar configuração

### Infrastructure Layer
- `ConfigurationMapper` - Conversão domínio/modelo
- `DjangoConfigurationRepository` - Implementação Django
- `ConfiguracaoGlobalAPIView` - API REST

## Testes

Execute os testes com:
```bash
python -m pytest tests/integration/test_django_configuration_repository.py -v
```