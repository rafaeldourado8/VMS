# 🚀 Comandos Git - Sprint 0

## Verificar mudanças

```bash
# Ver arquivos modificados
git status

# Ver diff detalhado
git diff
```

## Arquivos modificados

```
modified:   docker-compose.yml
modified:   backend/requirements.txt
modified:   backend/config/urls.py
modified:   backend/apps/cameras/views.py
modified:   .env.example
modified:   frontend/src/App.tsx
modified:   frontend/src/components/layout/Layout.tsx
modified:   docs/dvr-lite/CHECKLIST.md

new file:   docs/dvr-lite/SPRINT0_SUMMARY.md
new file:   docs/dvr-lite/TESTING_GUIDE.md
new file:   docs/dvr-lite/GIT_COMMANDS.md
```

## Commit

```bash
# Adicionar todos os arquivos
git add .

# Commit com mensagem descritiva
git commit -m "chore: setup dvr-lite branch - remove AI detection services

- Remove ai_detection and detection_consumer services from docker-compose
- Remove AI-related routes from backend (detections, AI control)
- Remove AI logic from camera creation and views
- Remove DetectionsPage and navigation menu item from frontend
- Update .env.example with DVR-focused variables
- Remove AI environment variables (YOLO, OCR, Rekognition configs)
- Add recording-related environment variables
- Update checklist and add documentation

This commit transforms the system into a pure DVR without AI detection,
preparing for recording and playback features in Sprint 1."

# Push para o repositório
git push origin dvr-lite
```

## Verificar commit

```bash
# Ver último commit
git log -1 --stat

# Ver diff do último commit
git show HEAD
```

## Criar Pull Request (opcional)

Se quiser revisar antes de mergear na main:

```bash
# No GitHub/GitLab, criar PR de dvr-lite → main
# Título: "DVR-Lite: Remove AI Detection Services (Sprint 0)"
# Descrição: Ver SPRINT0_SUMMARY.md
```

## Voltar para main (se necessário)

```bash
# Salvar trabalho atual
git stash

# Voltar para main
git checkout main

# Voltar para dvr-lite
git checkout dvr-lite

# Recuperar trabalho
git stash pop
```

## Desfazer mudanças (se necessário)

```bash
# Desfazer último commit (mantém mudanças)
git reset --soft HEAD~1

# Desfazer último commit (descarta mudanças)
git reset --hard HEAD~1

# Desfazer mudanças em arquivo específico
git checkout HEAD -- <arquivo>
```

## Tags (opcional)

```bash
# Criar tag para marcar Sprint 0
git tag -a v0.1.0-dvr-lite -m "Sprint 0: DVR-Lite setup complete"

# Push da tag
git push origin v0.1.0-dvr-lite
```

## Próximos passos

Após commit bem-sucedido:

1. Atualizar CHECKLIST.md:
   ```
   - [x] Testar que streaming ainda funciona
   - [x] Commit: "chore: setup dvr-lite branch"
   ```

2. Iniciar Sprint 1:
   ```bash
   # Criar branch para Sprint 1 (opcional)
   git checkout -b dvr-lite-sprint1
   ```

3. Começar implementação de Recording Service
