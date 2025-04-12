import subprocess
import socket
import atexit
import uuid
import sys
import os

_MANYTERM_HOST = '127.0.0.1'
_MANYTERM_PATH = os.path.abspath(__file__)

if sys.platform not in ["linux", "win32", "darwin"]:
    raise Exception(f"Platform \"{sys.platform}\" not supported for package manyterm")

class Server:
    running = False
    socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    connections = {}

    @staticmethod
    def start():
        """
        Start the server (if not already running)
        Returns:
            port (int): the port of the server
        """
        if not Server.running:
            Server.running = True
            Server.socket.bind((_MANYTERM_HOST, 0))
            atexit.register(Server.stop)
        return Server.socket.getsockname()[1]
    
    @staticmethod
    def send(uid, b):
        """
        Send a message(b) to a window based on the uid

        Args:
            uid (str): the uid of the window
            b (bytes): the message to send

        Returns:
            success (bool): whether the message was sent
        """
        addr = Server.connections.get(uid, None)
        if addr is not None:
            Server.socket.sendto(b, addr)
            return True
        else:
            return False
    
    @staticmethod
    def listen_for_input(uid):
        """
        Listens for input from a window based on the uid

        Args:
            uid (str): the uid of the window

        Returns:
            None
        """
        Server.socket.settimeout(None)
        expected = Server.connections.get(uid, None)
        data, addr = Server.socket.recvfrom(1024)
        if addr == expected:
            text = data.decode('utf-8')
            return text
        


    # listen for new connections
    @staticmethod
    def listen_for_client():
        """
        Listens for new connections to this server

        Returns:
            None
        """
        Server.socket.settimeout(15)
        data, addr = Server.socket.recvfrom(1024)
        if data is not None:
            text = data.decode('utf-8')
            Server.connections[text] = addr
        else:
            assert Exception("Could not bind window to server")


    @staticmethod
    def stop(): # close all windows
        for key in Server.connections:
            Server.socket.sendto(bytes("c", 'utf-8'), Server.connections.get(key))
        Server.socket.close()
        Server.running = False

class Terminal:
    def __init__(self, title="Terminal", cols=80, rows=24):
        """Start a new terminal window

            Args:
                title (str): the title of the window (linux only)
                cols (int): the width of the window
                rows (int): the height of the window

            Returns:
                object: Terminal object
        """

        # start server (if not running)
        server_port = Server.start()
        self._uid = str(uuid.uuid4())


        # open window
        if sys.platform == "linux":
            subprocess.run((
                'gnome-terminal',
                '--geometry', f'{cols}x{rows}',
                '-t', title,
                '--', 'bash', '-c',
                f'{sys.executable} {_MANYTERM_PATH} {server_port} {self._uid}'
            ), shell=False)
        elif sys.platform == "win32":
            size_command = f'mode con: cols={cols} lines={rows}'
            subprocess.Popen((
                'start', '/wait', 'cmd', '/c',
                f'{size_command} && {sys.executable} {_MANYTERM_PATH} {server_port} {self._uid}'
            ), shell=True)
        elif sys.platform == "darwin":
            #f'tell application "Terminal" to do script "printf \'\\e[8;{height};{width}t\'; {sys.executable} {_MANYTERM_PATH} {server_port} {self._uid}; exit"'
            subprocess.run(("osascript", "-e", f"tell application \"Terminal\" to do script \"{sys.executable} {_MANYTERM_PATH} {server_port} {self._uid};exit\""), shell=False)
    
        Server.listen_for_client()
        
        

    def print(self, txt, end="\n"):
        """
        Prints to the window

        Args:
            txt: the string to print
            end: the end of the string

        Returns:
            None
        """
        payload = bytes("p"+txt+end, 'utf-8')
        return Server.send(self._uid, payload)

    def input(self, txt):
        """
        Prints to the window

        Args:
            txt: the string to print
            end: the end of the string

        Returns:
            None
        """
        payload = bytes("i"+txt, 'utf-8')
        Server.send(self._uid, payload)
        return Server.listen_for_input(self._uid)

    def close(self):
        """
        Closes the window

        Returns:
            None
        """
        Server.send(self._uid, bytes("c", 'utf-8'))


if __name__ == '__main__':
    """
    Called from subprocess to open window
    Acts as a server to connect to the client and listens for data to print
    """
    if len(sys.argv) != 3:
        raise Exception("Usage: python3 oneToMany.py <port> <uid>")

    port = int(sys.argv[1])
    uid = sys.argv[2]

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(bytes(uid, 'utf-8'), (_MANYTERM_HOST, port))

    while True:
        data, addr = s.recvfrom(1024)
        text = data.decode('utf-8')
        if text[0] == "p":
            print(text[1:], end="")
        elif text[0] == "i":
            inp = input(text[1:])
            s.sendto(bytes(inp, 'utf-8'), (_MANYTERM_HOST, port))
        elif text[0] == "c":
            s.close()
            break
