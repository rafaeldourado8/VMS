// Healthcheck simples para o frontend
import http from 'http';

const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('OK');
  }
});

const PORT = 5174;
server.listen(PORT, () => {
  console.log(`Healthcheck server running on port ${PORT}`);
});
