"""Run this folder locally; no packages required. Python 3.9+."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from functools import partial
import webbrowser
root=Path(__file__).resolve().parent
handler=partial(SimpleHTTPRequestHandler,directory=str(root))
server=ThreadingHTTPServer(('127.0.0.1',8765),handler)
print('Booth viewer: http://127.0.0.1:8765 — Ctrl+C to stop')
webbrowser.open('http://127.0.0.1:8765')
try:server.serve_forever()
except KeyboardInterrupt:pass
finally:server.server_close()
