# Dockerfile (frontend builder) - com fallback para lockfile desatualizado
# ========================================
# Stage 1: Build do Frontend (Vite/React)
# ========================================
FROM node:20-alpine AS builder

ENV NODE_ENV=production
WORKDIR /app

# Dependências do sistema necessárias para algumas bibliotecas (ex: builds com sharp, etc.)
# (adapte se não precisar)
RUN apk add --no-cache python3 make g++ git

# Copia arquivos de dependências primeiro (melhor cache)
COPY package.json pnpm-lock.yaml* package-lock.json* yarn.lock* ./

# Habilita pnpm (se estiver usando)
RUN corepack enable && corepack prepare pnpm@latest --activate

# Instala dependências:
# - Tenta com --frozen-lockfile para builds reprodutíveis
# - Se falhar devido ao lockfile desatualizado, faz fallback para --no-frozen-lockfile e mostra mensagem
RUN set -e; \
    if [ -f pnpm-lock.yaml ]; then \
      echo "pnpm-lock.yaml detectado. Tentando pnpm install --frozen-lockfile"; \
      if pnpm install --frozen-lockfile; then \
        echo "pnpm install (frozen) concluído"; \
      else \
        echo "Aviso: pnpm install --frozen-lockfile falhou. Executando pnpm install --no-frozen-lockfile (FALLBACK)"; \
        pnpm install --no-frozen-lockfile; \
      fi; \
    elif [ -f package-lock.json ]; then \
      echo "package-lock.json detectado. Usando npm ci"; \
      npm ci; \
    elif [ -f yarn.lock ]; then \
      echo "yarn.lock detectado. Usando yarn install"; \
      yarn install --frozen-lockfile || yarn install; \
    else \
      echo "Nenhum lockfile detectado. Usando npm install"; \
      npm install; \
    fi

# Copia o código-fonte (depois de instalar dependências para aproveitar cache)
COPY . .

# Build do frontend (gera a pasta dist/)
RUN set -e; \
    if [ -f pnpm-lock.yaml ]; then \
      echo "Rodando pnpm build..."; \
      pnpm build; \
    elif [ -f package-lock.json ]; then \
      echo "Rodando npm run build..."; \
      npm run build; \
    elif [ -f yarn.lock ]; then \
      echo "Rodando yarn build..."; \
      yarn build; \
    else \
      echo "Rodando npm run build (fallback)..."; \
      npm run build; \
    fi; \
    echo "Conteúdo de /app/dist (após build):"; ls -lah /app/dist || true

# ========================================
# Stage 2: Artifacts (exporta o build)
# ========================================
FROM alpine:3.20 AS artifacts

WORKDIR /out

# Copia o conteúdo de dist/ diretamente para /out
COPY --from=builder /app/dist .

# Mantém o container rodando (opcional, para debug)
CMD ["tail", "-f", "/dev/null"]