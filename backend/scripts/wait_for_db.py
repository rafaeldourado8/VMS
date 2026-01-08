import socket
import time
import os
import sys

def wait_for_db():
    """Aguarda o banco de dados estar acessível via TCP"""
    host = os.environ.get("DB_HOST", "postgres_db")
    port = int(os.environ.get("DB_PORT", 5432))
    
    print(f"⏳ Aguardando PostgreSQL em {host}:{port}...")
    
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=1):
                print("✅ PostgreSQL está pronto!")
                return
        except (OSError, socket.error):
            pass
            
        if time.time() - start_time > 60:
            print("❌ Timeout aguardando o banco de dados.")
            sys.exit(1)
            
        time.sleep(1)
        print(".", end="", flush=True)

if __name__ == "__main__":
    wait_for_db()