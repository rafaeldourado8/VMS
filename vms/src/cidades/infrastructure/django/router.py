class MultiTenantRouter:
    """
    Router para multi-tenant: 1 DB por cidade
    
    - DB 'default': cities, users (admin)
    - DB 'cidade_{slug}': cameras, detections, recordings, etc
    """
    
    def db_for_read(self, model, **hints):
        # Models do app 'cidades' vão para default
        if model._meta.app_label == 'cidades':
            return 'default'
        
        # Outros apps vão para DB da cidade (via middleware)
        city_slug = self._get_current_city_slug()
        if city_slug:
            return f'cidade_{city_slug}'
        
        return 'default'
    
    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)
    
    def allow_relation(self, obj1, obj2, **hints):
        # Permite relações dentro do mesmo DB
        db1 = self.db_for_read(obj1.__class__)
        db2 = self.db_for_read(obj2.__class__)
        return db1 == db2
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Migrations de 'cidades' só no default
        if app_label == 'cidades':
            return db == 'default'
        
        # Outros apps migram em todos os DBs de cidades
        if db == 'default':
            return app_label == 'cidades'
        
        return db.startswith('cidade_')
    
    def _get_current_city_slug(self):
        # Implementar via middleware ou thread-local
        # Por enquanto retorna None
        return None
