import os
import random
import urllib.parse
from databases import Database
from sqlalchemy import MetaData, Table, Column, Integer, String, Float, JSON, DateTime, Boolean

# Credenciais (Lidas do ambiente Docker)
DB_USER = os.getenv("POSTGRES_USER", "user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DB_NAME = os.getenv("POSTGRES_DB", "vms_db")

# Hosts (Master e Replicas - Defaults para Docker local)
DB_HOST_WRITER = os.getenv("DB_HOST", "db")
# Simula réplicas apontando para o mesmo host se não definido
DB_HOST_READERS = os.getenv("DB_HOST_READERS", "db,db").split(",") 

# --- CORREÇÃO DE SEGURANÇA E URL ---
# Codifica usuário e senha para evitar erros com caracteres especiais (#, @, /, :)
DB_USER_ENCODED = urllib.parse.quote_plus(DB_USER)
DB_PASSWORD_ENCODED = urllib.parse.quote_plus(DB_PASSWORD)

# URLs de Conexão (Usando credenciais codificadas)
DATABASE_URL_WRITER = f"postgresql+asyncpg://{DB_USER_ENCODED}:{DB_PASSWORD_ENCODED}@{DB_HOST_WRITER}:5432/{DB_NAME}"

reader_urls = [
    f"postgresql+asyncpg://{DB_USER_ENCODED}:{DB_PASSWORD_ENCODED}@{host}:5432/{DB_NAME}" 
    for host in DB_HOST_READERS
]

# Instâncias de Conexão
database_writer = Database(DATABASE_URL_WRITER)
databases_readers = [Database(url) for url in reader_urls]

metadata = MetaData()

# Definição das Tabelas (Espelho do Django para o SQLAlchemy)
# CORREÇÃO: Tabela renomeada para 'cameras_camera' (app label 'cameras' + model 'Camera')
cameras_table = Table(
    "cameras_camera",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("stream_url", String),
    Column("status", String),
    Column("detection_settings", JSON),
)

# CORREÇÃO: Tabela renomeada para 'deteccoes_deteccao' e colunas traduzidas para Inglês
# para corresponder ao model Django (apps/deteccoes/models.py)
detections_table = Table(
    "deteccoes_deteccao", 
    metadata,
    Column("id", Integer, primary_key=True),
    Column("camera_id", Integer),
    Column("plate", String),       # Antes: placa
    Column("confidence", Float),   # Antes: confianca
    Column("timestamp", DateTime), # Antes: horario
    Column("image_url", String),   # Antes: imagem_url
    # Adicione outros campos conforme seu model Django se necessário
)

async def get_reader_db():
    """Retorna uma conexão de leitura aleatória (Load Balancer simples)"""
    return random.choice(databases_readers)

async def connect_dbs():
    await database_writer.connect()
    for db in databases_readers:
        await db.connect()

async def disconnect_dbs():
    await database_writer.disconnect()
    for db in databases_readers:
        await db.disconnect()