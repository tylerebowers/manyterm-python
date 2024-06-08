import subprocess
import socket
import atexit
import uuid
import sys
import os

_MANYTERM_PORT = 16161
_MANYTERM_HOST = '127.0.0.1'


if sys.platform not in ["linux", "win32", "darwin"]:
    raise Exception(f"Platform \"{sys.platform}\" not supported for package manyterm")

# server for sending text and listening for new connections
# all static methods so there is only one instance
class _Server:

    _running = False
    _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _connections = {}

    @staticmethod
    def start():
        if not _Server._running:
            _Server._running = True
            _Server._socket.bind((_MANYTERM_HOST, _MANYTERM_PORT))
            _Server._socket.settimeout(10)
            # close server and windows on exit
            atexit.register(_Server.stop)


    # listen for new connections
    @staticmethod
    def listen():
        data, addr = _Server._socket.recvfrom(1024)
        if data is not None:
            _Server._connections[data.decode('utf-8')] = addr
        else:
            assert Exception("Could not bind window to server")


    @staticmethod # print to a window based on the uid
    def send(uid, b):
        addr = _Server._connections.get(uid, None)
        if addr is not None:
            _Server._socket.sendto(b, addr)
        else:
            assert Exception("Cannot print to closed terminal")

    @staticmethod # close a window based on the uid
    def close(uid):
        _Server._socket.sendto(bytes(0), _Server._connections.get(uid))
        _Server._connections.pop(uid)

    @staticmethod
    def stop(): # close all windows
        for key in _Server._connections:
            _Server._socket.sendto(bytes(0), _Server._connections.get(key))
        _Server._socket.close()
        _Server._running = False


class Terminal:
    _path = os.path.abspath(__file__)

    def __init__(self, title="Terminal"):
        """
        Start a new terminal window
        :param title: the title of the window (linux only)
        """
        # start server (if not running)
        _Server.start()
        # make uid for self
        self._uid = str(uuid.uuid4())  # could also use uuid1()
        # open window
        if sys.platform == "linux":
            subprocess.run(('gnome-terminal', '-t', f'{title}', '--', 'bash', '-c', f'{sys.executable} {self._path} {self._uid}'), shell=False)
        elif sys.platform == "win32":
            subprocess.run(('start', '/wait','cmd', '/c', f'{sys.executable} {self._path} {self._uid}'), shell=True)
        elif sys.platform == "darwin":
            subprocess.run(("osascript", "-e", f"tell application \"Terminal\" to do script \"{sys.executable} {self._path} {self._uid};exit\""), shell=False)
        _Server.listen()  # wait for window to open and listen for new connection

    def print(self, txt, end="\n"):
        """
        Prints to the window
        :param txt: the string to print
        :param end: the end of the string
        """
        _Server.send(self._uid, bytes(txt+end, 'utf-8'))

    def close(self):
        """
        Closes the window
        """
        _Server.close(self._uid)

    def close_all(self):
        """
        Closes all windows
        """
        _Server.stop()


# called from subprocess to open window
# acts as a client to connect to the server and listens for data to print
class _TerminalClient:
    def __init__(self):
        if len(sys.argv) != 2:
            raise Exception("Usage: python3 manyterm.py <uid>")

        self._uid = sys.argv[1]

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # send uid to server
        s.sendto(bytes(self._uid, 'utf-8'), (_MANYTERM_HOST, _MANYTERM_PORT))

        while True:
            data, addr = s.recvfrom(1024)
            if data == bytes(0):
                break
            else:
                print(data.decode('utf-8'), end="")
        s.close()


if __name__ == '__main__':
    _TerminalClient()
