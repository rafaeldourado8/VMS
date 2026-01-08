"""
Script para criar índices otimizados no banco de dados
"""

# Índices para melhorar performance das queries mais comuns

INDEXES = [
    # Cameras - busca por owner e status
    "CREATE INDEX IF NOT EXISTS idx_cameras_owner_status ON cameras_camera(owner_id, status);",
    
    # Detecções - busca por timestamp e camera (queries de analytics)
    "CREATE INDEX IF NOT EXISTS idx_deteccoes_timestamp_camera ON deteccoes_deteccao(timestamp DESC, camera_id);",
    
    # Suporte - mensagens por usuário ordenadas por data
    "CREATE INDEX IF NOT EXISTS idx_suporte_autor_timestamp ON suporte_mensagem(autor_id, timestamp DESC);",
    
    # Clips - clips por owner ordenados por criação
    "CREATE INDEX IF NOT EXISTS idx_clips_owner_created ON clips_clip(owner_id, created_at DESC);",
    
    # Detecções - índice composto para analytics por período
    "CREATE INDEX IF NOT EXISTS idx_deteccoes_analytics ON deteccoes_deteccao(camera_id, timestamp, vehicle_type);",
]

def create_indexes():
    """Executa criação dos índices"""
    import sqlite3
    import os
    
    db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    
    if not os.path.exists(db_path):
        print("Banco de dados não encontrado")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for index_sql in INDEXES:
        try:
            cursor.execute(index_sql)
            print(f"OK Indice criado: {index_sql.split('idx_')[1].split(' ')[0]}")
        except Exception as e:
            print(f"ERRO ao criar indice: {e}")
    
    conn.commit()
    conn.close()
    print("Otimização de índices concluída")

if __name__ == "__main__":
    create_indexes()