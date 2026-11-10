"""Start .NEMA on the first available localhost port (no external dependencies)."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os
import threading
import webbrowser
os.chdir(Path(__file__).resolve().parent)
server = None
for port in range(8764, 8780):
    try:
        server = ThreadingHTTPServer(('127.0.0.1', port), SimpleHTTPRequestHandler)
        break
    except OSError:
        continue
if server is None:
    raise SystemExit('No free localhost port in 8764..8779')
url = f'http://127.0.0.1:{server.server_port}/website/index.html'
print('.NEMA website:', url, '\nPress Ctrl+C to stop.')
threading.Timer(0.5, lambda: webbrowser.open(url)).start()
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    server.server_close()
