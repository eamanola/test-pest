import tempfile
import os


# https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
def get_ip():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


CHOSTNAME = get_ip()
CPORT = 8086

CFFMPEG_STREAM = False
CFFMPEG_LEGLEVEL = "error"
CFFMPEG_HOST = CHOSTNAME
CFFMPEG_PORT = 8099

CTMP_DIR = os.path.join(tempfile.gettempdir(), "test-pest")
