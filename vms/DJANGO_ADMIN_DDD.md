# 🔍 Django Admin - Observabilidade Total (DDD)

## 📋 Princípio

**Django Admin é FERRAMENTA de observabilidade, NÃO é Domain.**

```
❌ ERRADO: Admin manipula dados diretamente
✅ CORRETO: Admin usa Use Cases do Domain
```

---

## 🏗️ Arquitetura

```
Django Admin (Infrastructure)
    ↓ usa
Use Cases (Application)
    ↓ usa
Entities (Domain)
```

**Admin NUNCA manipula entities diretamente!**

---

## ✅ Implementação Correta

### 1. List Display com Métodos Customizados

```python
@admin.register(UserModel)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "name", "is_admin", "is_active", "cities_count"]
    
    def cities_count(self, obj):
        """Observabilidade: quantas cidades o usuário acessa."""
        count = len(obj.city_ids)
        if obj.is_admin:
            return format_html('<span style="color: green;"><b>ADMIN (todas)</b></span>')
        return format_html(f'<span>{count} cidade(s)</span>')
```

**✅ Observabilidade:** Mostra informação derivada sem modificar dados.

---

### 2. Actions Usando Use Cases

```python
def activate_users(self, request, queryset):
    """Ativa usuários usando Use Case."""
    repo = DjangoUserRepository()
    
    for user_model in queryset:
        # 1. Busca entity
        user = repo.find_by_id(user_model.id)
        
        # 2. Usa método do domain
        user.activate()
        
        # 3. Persiste via repository
        repo.save(user)
    
    self.message_user(request, f"{queryset.count()} usuário(s) ativado(s)")
```

**✅ DDD:** Admin usa repository e entity methods, não manipula diretamente.

---

### 3. Filtros e Busca

```python
list_filter = ["is_admin", "is_active", "created_at"]
search_fields = ["email", "name"]
```

**✅ Observabilidade:** Permite encontrar dados rapidamente.

---

### 4. Fieldsets Organizados

```python
fieldsets = (
    ("Informações", {
        "fields": ("id", "email", "name")
    }),
    ("Segurança", {
        "fields": ("password_hash", "is_active")
    }),
    ("Permissões", {
        "fields": ("is_admin", "city_ids")
    }),
    ("Datas", {
        "fields": ("created_at", "updated_at")
    }),
)
```

**✅ Observabilidade:** Dados organizados por contexto.

---

## 🎯 Observabilidade Total

### O que o Admin DEVE mostrar:

1. **Status atual** - is_active, is_admin
2. **Métricas** - cities_count, detections_count
3. **Timestamps** - created_at, updated_at
4. **Relações** - city_ids, permissions
5. **Ações disponíveis** - activate, deactivate, promote

### O que o Admin NÃO DEVE fazer:

❌ Manipular entities diretamente  
❌ Ter lógica de negócio  
❌ Validações complexas  
❌ Cálculos de domínio  

**Tudo isso fica no Domain!**

---

## 📊 Exemplo Completo: Camera Admin

```python
@admin.register(CameraModel)
class CameraAdmin(admin.ModelAdmin):
    list_display = [
        "name", 
        "type", 
        "lpr_status", 
        "status", 
        "city",
        "detections_today"
    ]
    list_filter = ["type", "status", "city"]
    search_fields = ["name", "rtsp_url"]
    actions = ["activate_cameras", "deactivate_cameras", "enable_lpr"]
    
    def lpr_status(self, obj):
        """Observabilidade: LPR ativo?"""
        if obj.type == "rtsp":
            return format_html('<span style="color: green;">✓ Ativo</span>')
        return format_html('<span style="color: gray;">✗ Desativado</span>')
    lpr_status.short_description = "LPR"
    
    def detections_today(self, obj):
        """Observabilidade: detecções hoje."""
        # Usa repository para buscar
        from cameras.infrastructure.django.repository import DjangoDetectionRepository
        repo = DjangoDetectionRepository()
        count = repo.count_today(obj.id)
        return format_html(f'<b>{count}</b> detecções')
    detections_today.short_description = "Hoje"
    
    def activate_cameras(self, request, queryset):
        """Action usando Use Case."""
        from cameras.application.use_cases import ActivateCameraUseCase
        from cameras.infrastructure.django.repository import DjangoCameraRepository
        
        repo = DjangoCameraRepository()
        use_case = ActivateCameraUseCase(repo)
        
        for camera_model in queryset:
            try:
                use_case.execute(camera_model.id)
            except ValueError as e:
                self.message_user(request, str(e), level="ERROR")
        
        self.message_user(request, f"{queryset.count()} câmera(s) ativada(s)")
    activate_cameras.short_description = "Ativar câmeras"
```

---

## 🎯 Checklist DDD no Admin

### ✅ Correto
- [x] Admin usa Use Cases
- [x] Admin usa Repositories
- [x] Admin chama métodos de Entities
- [x] Admin mostra informações derivadas
- [x] Actions orquestram operações
- [x] Mensagens de feedback ao usuário

### ❌ Errado
- [ ] Admin manipula dados diretamente
- [ ] Admin tem lógica de negócio
- [ ] Admin faz validações complexas
- [ ] Admin conhece detalhes de persistência
- [ ] Admin modifica entities sem repository

---

## 📈 Métricas de Observabilidade

### User Admin
- Total de usuários
- Usuários ativos/inativos
- Admins vs normais
- Distribuição por cidade
- Últimos logins

### Camera Admin
- Total de câmeras
- Por tipo (RTSP/RTMP)
- Por status (ativa/inativa)
- LPR ativas
- Detecções por câmera

### Detection Admin
- Detecções hoje
- Por câmera
- Por confiança
- Blacklist matches
- Timeline

---

## 🚀 Benefícios

1. **Observabilidade Total** - Tudo visível no admin
2. **Controle Manual** - Actions para operações críticas
3. **DDD Mantido** - Admin não viola arquitetura
4. **Testável** - Use Cases testados isoladamente
5. **Manutenível** - Lógica no domain, não no admin

---

## 📝 Exemplo de Uso

### Cenário: Ativar 10 câmeras

**❌ Errado (sem DDD):**
```python
def activate_cameras(self, request, queryset):
    queryset.update(status='active')  # Manipula diretamente
```

**✅ Correto (com DDD):**
```python
def activate_cameras(self, request, queryset):
    repo = DjangoCameraRepository()
    use_case = ActivateCameraUseCase(repo)
    
    for camera_model in queryset:
        camera = repo.find_by_id(camera_model.id)
        camera.activate()  # Método do domain
        repo.save(camera)
```

---

**Princípio:** Django Admin é FERRAMENTA, não DOMAIN.

**Criado:** 2024  
**Versão:** 1.0.0
