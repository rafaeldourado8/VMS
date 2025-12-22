import random

class PrimaryReplicaRouter:
    def db_for_read(self, model, **hints):
        """
        Leituras vão para a réplica disponível. 
        Como temos apenas uma, retornamos 'replica1'.
        """
        # Se você adicionar 'replica2' no settings futuramente, 
        # mude para: return random.choice(['replica1', 'replica2'])
        return 'replica1'

    def db_for_write(self, model, **hints):
        """
        Escritas sempre vão para o banco principal (MASTER).
        """
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Permite relações se ambos os objetos estiverem no pool conhecido.
        """
        db_list = ('default', 'replica1')
        if obj1._state.db in db_list and obj2._state.db in db_list:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Garante que migrações ocorram preferencialmente no banco master.
        """
        if db == 'replica1':
            return False
        return True