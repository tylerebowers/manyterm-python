import manyterm
from time import sleep


#make new terminals
t1 = manyterm.Terminal()
t2 = manyterm.Terminal(title="Customized Title (t2)")
#sleep(5)

#use the new terminals
for i in range(21):
    print(f"Main terminal: {i}")
    t1.print(f"Terminal 1: {i}")
    t2.print(f"Terminal 2: {i}")
    sleep(0.2)

t1.print("This is Terminal 1")
t2.print("This is Terminal 2")
t2.print("This is a long line to show that the text will wrap around to the next line. Here is some more text so that I can actually make the entire length.")
print("This is the main terminal")

# close terminal 1
print("Closing terminal 1 in 10 seconds.")
sleep(10)
t1.close()
print("Closed terminal 1")

t1.print("Closed prints will not do anything.")  # no errors thrown since user can close at any time

# close terminal 2 on exit
print("Exiting in 10 seconds, terminal 2 will close when the main program exits.")
sleep(10)
quit()