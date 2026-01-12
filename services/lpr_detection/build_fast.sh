#!/bin/bash
# Build rápido do LPR Detection Service

echo "🚀 Build Rápido - LPR Detection"
echo "================================"

# Usar BuildKit para cache
export DOCKER_BUILDKIT=1

# Build com cache
docker build \
  --file Dockerfile.optimized \
  --tag gtvision/lpr_detection:latest \
  --cache-from gtvision/lpr_detection:latest \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  .

echo "✅ Build concluído!"
echo "Tamanho da imagem:"
docker images gtvision/lpr_detection:latest --format "{{.Size}}"
