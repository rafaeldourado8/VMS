# 1. Imagem base
FROM python:3.10-slim

# 2. Define variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Define o diretório de trabalho
WORKDIR /app

# 4. Atualiza o pip
RUN pip install --upgrade pip

# --- CORREÇÃO AQUI ---
# 5. COPIE o requirements.txt primeiro
COPY requirements.txt .

# 6. INSTALE as dependências
RUN pip install -r requirements.txt
# ---------------------

# 7. Copie o resto do seu código
COPY . .

# O 'command' (gunicorn) já está no seu docker-compose.yml