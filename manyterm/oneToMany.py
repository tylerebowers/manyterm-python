import socket
import atexit
import struct
import uuid
import sys
import os


_MANYTERM_HOST = '127.0.0.1'
_MANYTERM_PATH = os.path.abspath(__file__)

if sys.platform not in ["linux", "win32", "darwin"]:
    raise Exception(f"Platform \"{sys.platform}\" not supported for package manyterm")

def _send(conn, b):
    conn.sendall(struct.pack('!I', len(b)) + b)

def _recv_exact(conn, n):
    buf = bytearray()
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return bytes(buf)

def _recv(conn):
    head = _recv_exact(conn, 4)
    if head is None:
        return None
    return _recv_exact(conn, struct.unpack('!I', head)[0])

class Server:
    running = False
    socket = None
    connections = {}

    @staticmethod
    def start():
        if not Server.running:
            Server.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            Server.socket.bind((_MANYTERM_HOST, 0))
            Server.socket.listen(16)
            Server.running = True
            atexit.register(Server.stop)
        return Server.socket.getsockname()[1]

    @staticmethod
    def accept(uid, timeout=15):
        Server.socket.settimeout(timeout)
        while True:
            conn, _ = Server.socket.accept()      # raises socket.timeout
            conn.settimeout(None)
            hello = _recv(conn)
            if hello is None:
                conn.close()
                continue
            Server.connections[hello.decode()] = conn
            if hello.decode() == uid:
                return

    @staticmethod
    def _drop(uid):
        conn = Server.connections.pop(uid, None)
        if conn:
            conn.close()

    @staticmethod
    def request(uid, b):
        """Send and wait for the window's reply. None means the window is gone."""
        conn = Server.connections.get(uid)
        if conn is None:
            return None
        try:
            _send(conn, b)
            reply = _recv(conn)
        except OSError:
            reply = None
        if reply is None:
            Server._drop(uid)
        return reply

    @staticmethod
    def stop():
        for uid in list(Server.connections):
            conn = Server.connections[uid]
            try:
                _send(conn, b'c')
            except OSError:
                pass
            conn.close()
        Server.connections.clear()
        if Server.socket:
            Server.socket.close()
        Server.running = False

class Terminal:
    def __init__(self, title="Terminal", cols=80, rows=24, terminal=None):
        """Start a new terminal window

            Args:
                title (str): the title of the window (linux only)
                cols (int): the width of the window
                rows (int): the height of the window
                terminal (str): ["gnome", "kde", "konsole", "kitty", "alacritty"] the terminal to use (linux only)

            Returns:
                object: Terminal object
        """
        from .util import open_terminal

        # start server (if not running)
        server_port = Server.start()
        self._uid = str(uuid.uuid4())

        # open window
        cmd = f'{sys.executable} {_MANYTERM_PATH} {server_port} {self._uid}'
        open_terminal(cmd, title, cols, rows, terminal)
    
        Server.accept(self._uid)
        
        

    def print(self, txt, end="\n"):
        """
        Prints to the window

        Args:
            txt: the string to print
            end: the end of the string

        Returns:
            None
        """
        return Server.request(self._uid, b'p' + (txt + end).encode()) == b'ok'

    def input(self, txt):
        """
        Prints to the window

        Args:
            txt: the string to print
            end: the end of the string

        Returns:
            None
        """
        reply = Server.request(self._uid, b'i' + txt.encode())
        return reply.decode() if reply is not None else None

    def close(self):
        """
        Closes the window

        Returns:
            None
        """
        conn = Server.connections.get(self._uid)
        if conn:
            try:
                _send(conn, b'c')          # fire and forget, no reply expected
            except OSError:
                pass
            Server._drop(self._uid)


if __name__ == '__main__':
    """
    Called from subprocess to open window
    Acts as a server to connect to the client and listens for data to print
    """
    if len(sys.argv) != 3:
        raise Exception("Usage: python3 oneToMany.py <port> <uid>")

    port = int(sys.argv[1])
    uid = sys.argv[2]

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((_MANYTERM_HOST, port))
    _send(s, uid.encode())

    while True:
        msg = _recv(s)
        if msg is None or msg[:1] == b'c':
            break
        kind, body = msg[:1], msg[1:].decode('utf-8')
        if kind == b'p':
            print(body, end="", flush=True)
            _send(s, b'ok')
        elif kind == b'i':
            _send(s, input(body).encode('utf-8'))
    s.close()
