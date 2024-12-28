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


class _Server:
    """
    Server hosted by the running package to handle connections to windows
    """

    _running = False
    _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _connections = {}

    @staticmethod
    def start():
        """
        Start the server (if not already running)

        Returns:
            None
        """
        if not _Server._running:
            _Server._running = True
            _Server._socket.bind((_MANYTERM_HOST, _MANYTERM_PORT))
            _Server._socket.settimeout(10)
            # close server and windows on exit
            atexit.register(_Server.stop)


    # listen for new connections
    @staticmethod
    def listen():
        """
        Listens for new connections to this server

        Returns:
            None
        """
        data, addr = _Server._socket.recvfrom(1024)
        if data is not None:
            _Server._connections[data.decode('utf-8')] = addr
        else:
            assert Exception("Could not bind window to server")


    @staticmethod
    def send(uid, b):
        """
        Send a message(b) to a window based on the uid

        Args:
            uid (str): the uid of the window
            b (bytes): the message to send

        Returns:
            None
        """
        addr = _Server._connections.get(uid, None)
        if addr is not None:
            _Server._socket.sendto(b, addr)
        else:
            assert Exception("Cannot print to closed terminal")

    @staticmethod
    def close(uid):
        """
        Closes a window based on the uid

        Args:
            uid (str): the uid of the window

        Returns:
            None
        """
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
        """Start a new terminal window

            Args:
                title (str): the title of the window (linux only)

            Returns:
                object: Terminal object
        """
        # start server (if not running)
        _Server.start()
        # make uid for self
        self._uid = str(uuid.uuid4())  # could also use uuid1()
        # open window
        if sys.platform == "linux":
            subprocess.run(('gnome-terminal', '-t', f'{title}', '--', 'bash', '-c', f'{sys.executable} {self._path} {self._uid}'), shell=False)
        elif sys.platform == "win32":
            subprocess.Popen(('start', '/wait','cmd', '/c', f'{sys.executable} {self._path} {self._uid}'), shell=True)
        elif sys.platform == "darwin":
            subprocess.run(("osascript", "-e", f"tell application \"Terminal\" to do script \"{sys.executable} {self._path} {self._uid};exit\""), shell=False)
        _Server.listen()  # wait for window to open and listen for new connection

    def print(self, txt, end="\n"):
        """
        Prints to the window

        Args:
            txt: the string to print
            end: the end of the string

        Returns:
            None
        """
        _Server.send(self._uid, bytes(txt+end, 'utf-8'))

    def close(self):
        """
        Closes the window

        Returns:
            None
        """
        _Server.close(self._uid)

    def close_all(self):
        """
        Closes all windows

        Returns:
            None
        """
        _Server.stop()


class _TerminalClient:
    def __init__(self):
        """
        Called from subprocess to open window
        Acts as a client to connect to the server and listens for data to print

        Returns:
            None
        """
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
