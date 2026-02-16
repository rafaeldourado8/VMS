# Teste de Criação de Câmera

## Checklist:

1. ✅ **Você está logado no sistema?**
   - Vá para http://localhost/login
   - Faça login com suas credenciais
   - Verifique se aparece seu nome no canto superior direito

2. ✅ **Dados mínimos para criar câmera:**
   ```json
   {
     "name": "Teste",
     "stream_url": "rtsp://admin:admin@192.168.1.100:554/stream",
     "location": "Teste",
     "recording_retention_days": 30
   }
   ```

3. ✅ **Abra o Console do Navegador (F12)**
   - Aba "Console"
   - Veja os logs: "Creating camera with data:"
   - Veja o erro: "Error creating camera:"

4. ✅ **Possíveis erros:**
   - **401 Unauthorized** → Você não está logado
   - **400 Bad Request** → Campo obrigatório faltando ou inválido
   - **503 Service Unavailable** → Backend não está respondendo

## Como testar:

1. Faça login
2. Vá para "Câmeras"
3. Clique em "Adicionar Câmera"
4. Escolha "Modo Avançado"
5. Preencha:
   - Nome: `Teste`
   - URL: `rtsp://admin:admin@192.168.1.100:554/stream`
   - Localização: `Teste`
   - Retenção: `30 dias`
6. Clique em "Criar Câmera"
7. Veja o console (F12)

## Se ainda der erro 400:

Copie e cole aqui o que aparece no console:
- "Creating camera with data: ..."
- "Error creating camera: ..."
