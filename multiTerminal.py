from time import sleep
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading


class terminal(threading.Thread):

    def __init__(self, title="Terminal", height=20, width=100, font=("Courier New", "12")):
        self.title = title
        self.height = height
        self.width = width
        self.font = font
        self.root = None
        self.st = None
        threading.Thread.__init__(self, daemon=True)  # kill child thread on main thread exit
        self.start()
        sleep(0.5)  # wait for window to open

    def close(self):
        if self.root is not None:
            self.root.quit()
            self.root.update()
            self.root = None
            self.st = None

    def run(self):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.title(self.title)
        self.st = ScrolledText(self.root, height=self.height, width=self.width, font=self.font)
        self.st.pack()
        self.root.mainloop()

    def print(self, toPrint):
        if self.root is None or self.st is None:
            raise Exception(f"Terminal \"{self.title}\" is closed")
            #print(f"Terminal {self.title} is closed")
        else:
            self.st.configure(state="normal")
            self.st.see("end")  # show last line printed (could also put this under "insert" but there would be a gap)
            self.st.insert("end", toPrint)
            self.st.configure(state="disabled")
