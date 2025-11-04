# 1. Imagem Base
# Usamos a 'slim' que é leve
FROM python:3.10-slim

# 2. Configurações de Ambiente do Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Define o diretório de trabalho DENTRO do container
WORKDIR /app

# 4. Instala as dependências
# Copia SÓ o requirements.txt primeiro (para usar o cache do Docker)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia o resto do código do seu projeto
COPY . /app/

# (Não precisamos do CMD ou EXPOSE, o docker-compose vai cuidar disso)