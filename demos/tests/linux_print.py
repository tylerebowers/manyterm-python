import manyterm 
from time import sleep


#make new terminals
g = manyterm.Terminal(terminal="gnome")
k = manyterm.Terminal(terminal="kde")
ki = manyterm.Terminal(terminal="kitty")
a = manyterm.Terminal(terminal="alacritty")

g.print("Hello from gnome!")
k.print("Hello from kde!")
ki.print("Hello from kitty!")
a.print("Hello from alacritty!")
print("Hello from the main terminal!")

print("Exiting in 20 seconds, all terminals will close when the main program exits.")
sleep(20)
