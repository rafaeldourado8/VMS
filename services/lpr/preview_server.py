import http.server
import socketserver
import os

os.chdir('/app/snapshots')

PORT = 8090

Handler = http.server.SimpleHTTPRequestHandler
Handler.extensions_map['.jpg'] = 'image/jpeg'

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Servidor rodando na porta {PORT}", flush=True)
    httpd.serve_forever()
