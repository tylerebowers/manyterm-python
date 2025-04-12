import subprocess
import socket
import sqlite3
import psutil
import uuid
import time
import sys
import os

_MANYTERM_HOST = '127.0.0.1'
_MANYTERM_DB = os.path.expanduser("~/.manyterm.db")
_MANYTERM_PATH = os.path.abspath(__file__)

if sys.platform not in ["linux", "win32", "darwin"]:
    raise Exception(f"Platform \"{sys.platform}\" not supported for package manyterm")

class SharedTerminal:
    def __init__(self, uid, title="Terminal", cols=80, rows=24):
        """Start a new terminal window

            Args:
                title (str): the title of the window (used during creation only)
                cols (int): the width of the window (used during creation only)
                rows (int): the height of the window (used during creation only)
                uid (str): the uid of the window (used to open an existing window)

            Returns:
                object: Terminal object
        """
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._uid = str(uuid.uuid4())
        self._window_uid = str(uuid.uuid4()) if uid is None else uid
        self._port = -1 # to be set below

        self._db = sqlite3.connect(_MANYTERM_DB)
        self._db_cursor = self._db.cursor()

        self._db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS windows (
                uid TEXT PRIMARY KEY,
                port INTEGER
            )
        ''')

        existing = self._db_cursor.execute(f"SELECT * FROM windows WHERE uid = '{self._window_uid}'").fetchone()
        if existing is not None:
            #get port
            self._port = existing[1]
            #make sure it is actually in use
            for conn in psutil.net_connections(): 
                if conn.laddr.port == self._port:
                    self._send(bytes("n"+self._uid, 'utf-8'))  
                    return # already open so just return
            # if here then there is a dirty record in the DB
            self._db_cursor.execute(f"DELETE FROM windows WHERE uid = '{self._window_uid}'")
            self._db.commit()


        # open window
        if sys.platform == "linux":
            subprocess.run((
                'gnome-terminal',
                '--geometry', f'{cols}x{rows}',
                '-t', title,
                '--', 'bash', '-c',
                f'{sys.executable} {_MANYTERM_PATH} {self._window_uid}'
            ), shell=False)
        elif sys.platform == "win32":
            size_command = f'mode con: cols={cols} lines={rows}'
            subprocess.Popen((
                'start', '/wait', 'cmd', '/c',
                f'{size_command} && {sys.executable} {_MANYTERM_PATH} {self._window_uid}'
            ), shell=True)
        elif sys.platform == "darwin":
            apple_script = (
                f'tell application "Terminal" to do script '
                f'"printf \'\\e[8;{height};{width}t\'; {sys.executable} {_MANYTERM_PATH} {self._window_uid}; exit"'
            )
            subprocess.run(("osascript", "-e", apple_script), shell=False)

        for i in range(100): # wait for window to open (max 10s)... better way to do this? --> make a PR.
            self._port = self._get_port_from_db()
            if self._port > 0: break
            time.sleep(0.1)
        
        if self._port == -1:
            raise Exception("Failed to open window")

        self._send(bytes("n"+self._uid, 'utf-8'))  
        
        
    def _get_port_from_db(self):
        query = self._db_cursor.execute(f"SELECT * FROM windows WHERE uid = '{self._window_uid}'").fetchone()
        if query is not None:
            return query[1]
        else:
            return -1

    def _send(self, b):
        self._port = self._port if self._port > 0 else self._get_port_from_db()
        self._socket.sendto(b, (_MANYTERM_HOST, self._port))


    def print(self, txt, end="\n"):
        """
        Prints to the window

        Args:
            txt: the string to print
            end: the end of the string

        Returns:
            None
        """
        self._send(bytes("p"+txt+end, 'utf-8'))     

    def close(self):
        """
        Closes the window

        Returns:
            None
        """
        self._send(bytes("c", 'utf-8'))


if __name__ == '__main__':
    """
    Called from subprocess to open window
    Acts as a server to connect to the client and listens for data to print
    """
    import atexit

    if len(sys.argv) != 2:
        raise Exception("Usage: python3 manyToOne.py <uid>")

    uid = sys.argv[1]

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((_MANYTERM_HOST, 0))

    db = sqlite3.connect(_MANYTERM_DB)
    db_cursor = db.cursor()
    db_cursor.execute(f"INSERT OR REPLACE INTO windows (uid, port) VALUES (?, ?)", (uid, s.getsockname()[1]))
    db.commit()

    def close():
        db_cursor.execute(f"DELETE FROM windows WHERE uid = '{uid}'")
        db.commit()
        s.close()

    atexit.register(close) # not called if window closed via the "x" button

    connections = {}
    while True:
        data, addr = s.recvfrom(1024)
        text = data.decode('utf-8')
        if text[0] == "p":
            print(text[1:], end="")
        elif text[0] == "n":
            connections[text[1:]] = addr
        elif text[0] == "c":
            close()
            break
