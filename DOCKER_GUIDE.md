# 🐳 Docker Compose - Guia de Uso

## 📋 Arquivos

- **docker-compose.yml** - Serviços principais (leve e rápido)
- **docker-compose.ai.yml** - Serviço de IA (pesado, build separado)

## 🚀 Como usar

### 1. Subir serviços principais (sem IA)
```bash
docker-compose up -d
```

### 2. Construir e subir o serviço de IA (separadamente)
```bash
# Apenas construir a imagem
docker-compose -f docker-compose.ai.yml build

# Subir o serviço
docker-compose -f docker-compose.ai.yml up -d
```

### 3. Subir tudo junto (se necessário)
```bash
docker-compose -f docker-compose.yml -f docker-compose.ai.yml up -d
```

## 🛑 Parar serviços

### Parar apenas serviços principais
```bash
docker-compose down
```

### Parar apenas IA
```bash
docker-compose -f docker-compose.ai.yml down
```

### Parar tudo
```bash
docker-compose -f docker-compose.yml -f docker-compose.ai.yml down
```

## 💡 Vantagens dessa separação

✅ Build mais rápido dos serviços principais  
✅ Desenvolvimento sem precisar da IA rodando  
✅ Economia de recursos quando IA não é necessária  
✅ Facilita testes e debugging  
✅ Deploy independente dos componentes
