import selectors
import socket
import sqlite3
import struct
import uuid
import time
import sys
import os

_MANYTERM_HOST = '127.0.0.1'
_MANYTERM_DB = os.path.expanduser("~/.manyterm.db")
_MANYTERM_PATH = os.path.abspath(__file__)

if sys.platform not in ["linux", "win32", "darwin"]:
    raise Exception(f"Platform \"{sys.platform}\" not supported for package manyterm")

_SCHEMA = "CREATE TABLE IF NOT EXISTS windows (uid TEXT PRIMARY KEY, port INTEGER)"


def _frame(b):
    return struct.pack('!I', len(b)) + b


class SharedTerminal:
    def __init__(self, uid=None, title="Terminal", cols=80, rows=24, terminal=None):
        """Attach to a shared terminal window, opening one if needed.

            Args:
                uid (str): the uid of the window (pass an existing uid to attach)
                title (str): the title of the window (creation only)
                cols (int): the width of the window (creation only)
                rows (int): the height of the window (creation only)
                terminal (str): ["gnome", "kde", "konsole", "kitty", "alacritty"] (linux only)
        """
        from .util import open_terminal

        self._window_uid = str(uuid.uuid4()) if uid is None else uid
        self._sock = None

        self._db = sqlite3.connect(_MANYTERM_DB)
        self._db.execute(_SCHEMA)
        self._db.commit()

        port = self._port_from_db()
        if port is not None:
            if self._connect(port):
                return
            self._forget()  # stale record, window is gone

        cmd = f'{sys.executable} {_MANYTERM_PATH} {self._window_uid}'
        proc = open_terminal(cmd, title, cols, rows, terminal)

        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            port = self._port_from_db()
            if port is not None and self._connect(port):
                return
            if proc is not None and proc.poll() not in (None, 0):
                raise Exception(f"Terminal exited with code {proc.returncode}")
            time.sleep(0.05)

        raise Exception("Failed to open window")

    #### discovery ####

    def _port_from_db(self):
        row = self._db.execute(
            "SELECT port FROM windows WHERE uid = ?", (self._window_uid,)
        ).fetchone()
        return row[0] if row else None

    def _forget(self):
        self._db.execute("DELETE FROM windows WHERE uid = ?", (self._window_uid,))
        self._db.commit()

    def _connect(self, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        try:
            s.connect((_MANYTERM_HOST, port))
        except OSError:
            s.close()
            return False
        s.settimeout(None)
        self._sock = s
        return True

    #### communication ####

    def _request(self, b, expect_reply=True):
        if self._sock is None:
            return None
        try:
            self._sock.sendall(_frame(b))
            if not expect_reply:
                return b''
            head = self._recv_exact(4)
            if head is None:
                raise OSError
            return self._recv_exact(struct.unpack('!I', head)[0])
        except OSError:
            self._sock.close()
            self._sock = None
            self._forget()
            return None

    def _recv_exact(self, n):
        buf = bytearray()
        while len(buf) < n:
            chunk = self._sock.recv(n - len(buf))
            if not chunk:
                return None
            buf += chunk
        return bytes(buf)

    def print(self, txt, end="\n"):
        """Print to the window. Returns True once the window has printed it."""
        return self._request(b'p' + (txt + end).encode('utf-8')) == b'ok'

    def close(self):
        """Close the window for every attached client."""
        self._request(b'c', expect_reply=False)
        self.detach()

    def detach(self):
        """Disconnect without closing the window."""
        if self._sock is not None:
            self._sock.close()
            self._sock = None
        self._db.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.detach()


if __name__ == '__main__':
    import atexit
    import signal

    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 manyToOne.py <uid>")
    uid = sys.argv[1]

    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((_MANYTERM_HOST, 0))
    lsock.listen(64)

    db = sqlite3.connect(_MANYTERM_DB)
    db.execute(_SCHEMA)
    db.execute("INSERT OR REPLACE INTO windows (uid, port) VALUES (?, ?)",
               (uid, lsock.getsockname()[1]))
    db.commit()

    def cleanup():
        try:
            db.execute("DELETE FROM windows WHERE uid = ?", (uid,))
            db.commit()
            db.close()
        except Exception:
            pass
        lsock.close()

    atexit.register(cleanup)
    for name in ("SIGHUP", "SIGTERM", "SIGINT"):
        if hasattr(signal, name):
            signal.signal(getattr(signal, name), lambda *_: sys.exit(0))

    sel = selectors.DefaultSelector()
    sel.register(lsock, selectors.EVENT_READ)
    buffers = {}
    running = True

    while running:
        for key, _ in sel.select():
            if key.fileobj is lsock:
                conn, _addr = lsock.accept()
                conn.setblocking(False)
                buffers[conn] = bytearray()
                sel.register(conn, selectors.EVENT_READ)
                continue

            conn = key.fileobj
            try:
                chunk = conn.recv(65536)
            except OSError:
                chunk = b''
            if not chunk:                      # client went away
                sel.unregister(conn)
                buffers.pop(conn, None)
                conn.close()
                continue

            buf = buffers[conn]
            buf += chunk
            while len(buf) >= 4:
                (n,) = struct.unpack('!I', buf[:4])
                if len(buf) < 4 + n:
                    break
                msg = bytes(buf[4:4 + n])
                del buf[:4 + n]

                if msg[:1] == b'p':
                    print(msg[1:].decode('utf-8'), end="", flush=True)
                    try:
                        conn.sendall(_frame(b'ok'))
                    except OSError:
                        pass
                elif msg[:1] == b'c':
                    running = False

    cleanup()