import socketserver
import subprocess
import sys
from CONFIG import CHOSTNAME, CPORT, CTMP_DIR
from api.streamingrequesthandler import StreamingRequestHandler

hostName = CHOSTNAME
serverPort = CPORT
socketserver.ThreadingTCPServer.allow_reuse_address = True
httpd = socketserver.ThreadingTCPServer(
    (hostName, serverPort), StreamingRequestHandler
)

print(f"Server started http://{hostName}:{serverPort}")
try:
    httpd.daemon_threads = True
    subprocess.Popen([
        'firefox',
        # 'chromium',
        # f'file:///data/tmp/Media%20Server/html/index.html?api_url=http://{hostName}:{serverPort}'
        f'http://{hostName}:{serverPort}'
    ])
    httpd.serve_forever()
except KeyboardInterrupt:
    pass

finally:
    httpd.server_close()
    print("Server stopped.")

    import shutil
    import os
    if os.path.exists(CTMP_DIR):
        shutil.rmtree(CTMP_DIR)

sys.exit(0)
