import subprocess
import sys

platform = sys.platform

def open_terminal(cmd, title="Terminal", cols=80, rows=24, terminal="kde"):
    if terminal is None: terminal = "kde" # other OSes don't have other options
    if platform == "linux":
        if terminal in ["kde", "konsole"]: #https://docs.kde.org/stable_kf6/en/konsole/konsole/command-line-options.html
            return subprocess.Popen((
                'konsole',
                '--hide-menubar',
                '--hide-tabbar',
                '--hide-toolbars',
                '-p', f'TerminalColumns={cols}',
                '-p', f'TerminalRows={rows}',
                '-p', f'tabtitle={title}',
                '-e', 'bash', '-c', cmd
            ), shell=False)
        elif terminal == "gnome":
            subprocess.run((
                'gnome-terminal',
                '--hide-menubar',
                '--geometry', f'{cols}x{rows}',
                '-t', title,
                '--', 'bash', '-c',
                cmd
            ), shell=False)
        elif terminal == "kitty": #https://sw.kovidgoyal.net/kitty/invocation/
            return subprocess.Popen((
                'kitty',
                '--title', title,
                '-o', 'remember_window_size=no',
                '-o', f'initial_window_width={cols}c',
                '-o', f'initial_window_height={rows}c',
                'bash', '-c', cmd
            ), shell=False)
        elif terminal == "alacritty": #https://alacritty.org/cmd-alacritty.html
            return subprocess.Popen((
                'alacritty',
                '--title', title,
                '-o', f'window.dimensions.columns={cols}',
                '-o', f'window.dimensions.lines={rows}',
                '-e', 'bash', '-c', cmd
            ), shell=False)
        else:
            raise Exception(f"Terminal \"{terminal}\" not supported for platform \"{platform}\"")
    elif platform == "win32":
        size_command = f'mode con: cols={cols} lines={rows}'
        return subprocess.Popen((
            'start', '/wait', 'cmd', '/c',
            f'{size_command} && {cmd}'
        ), shell=True)
    elif platform == "darwin":
        #f'tell application "Terminal" to do script "printf \'\\e[8;{height};{width}t\'; {sys.executable} {_MANYTERM_PATH} {server_port} {self._uid}; exit"'
        subprocess.run(("osascript", "-e", f"tell application \"Terminal\" to do script \"{cmd};exit\""), shell=False)
    else:
        raise Exception(f"Platform \"{platform}\" not supported for package manyterm")