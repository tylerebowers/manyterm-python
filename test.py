from multiTerminal import terminal
from time import sleep


#make new terminals
t1 = terminal()
t2 = terminal(title="Customized Terminal", height=30, width=80, font=("Arial", "20"))

#use the new terminals
for i in range(51):
    print(f"Main terminal: {i}")
    t1.print(f"Terminal 1: {i}")
    t2.print(f"Terminal 2: {i}")
    sleep(0.1)

t1.print("This is Terminal 1")
t2.print("This is Terminal 2")
t2.print("This is a long line to show that the text will not wrap around to the next line. Here is some more text so that I can actually make the entire length.")
print("This is the main terminal")

# close terminal 1
print("Closing terminal 1 in 5 seconds.")
sleep(5)
t1.close()
sleep(1)
print("If terminal 1 is closed (and ignoreAfterClose is False (default)), then t1.print attempts will be redirected to main terminal.")
t1.print("This line was printed to Terminal 1 but it was redirected to the main terminal. This is because terminal 1 was closed.")
sleep(5)

# close terminal 2 on exit
print("Exiting in 5 seconds, terminal 2 will close when the main program exits.")
sleep(5)
quit()