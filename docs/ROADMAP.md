📌 Fase 1 — MVP (até 20/01)

Streaming ao vivo estável

Lista de câmeras

Mosaico 2x2

IA para detecção de placas

Registro básico de eventos

Controle de usuários

📌 Fase 2 — Operação Avançada

Playback

Recorte de vídeo

Histórico por câmera

Exportação de clipes

Melhorias de UI/UX

📌 Fase 3 — Analytics e Escala

Dashboards analíticos

Relatórios

Otimização de IA local

Multi-tenant avançado

Integração com outros sistemas

🧩 GitHub Issues — Quebra de Tarefas
🟢 Backend

 Limitar streams simultâneos por cliente

 Endpoint de eventos de IA

 Persistência de eventos (placas)

 Controle de usuários simultâneos

 Healthcheck de serviços

🟡 IA

 Captura de frames via FFmpeg (1 FPS)

 Integração com AWS Rekognition / modelo local

 Publicação de eventos

 Circuit breaker por CPU

🔵 Frontend

 Lista de câmeras

 Player de vídeo unificado

 Mosaico 2x2 fixo

 Indicador de IA ativa

 Tela simples de eventos

⚙️ Infra

 Limites de processos FFmpeg

 Monitoramento básico de CPU/RAM

 Logs estruturados

 Docker-compose otimizado para produção

🏛️ Texto para Apresentação à Prefeitura (curto)

“O sistema permite a visualização ao vivo de câmeras com alta qualidade de vídeo e inteligência artificial integrada para detecção automática de eventos.
A IA funciona de forma independente, sem impactar o streaming, garantindo estabilidade e operação contínua.
A plataforma é segura, escalável e preparada para evolução futura, como playback e relatórios.”