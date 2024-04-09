from multiTerminal import terminal
from time import sleep


#make new terminals
t1 = terminal()
t2 = terminal(title="Customized Terminal", height=30, width=80, font=("Arial", "16"))

#use the new terminals
for i in range(11):
    print(f"Main terminal: {i}")
    t1.print(f"Terminal 1: {i}\n")
    t2.print(f"Terminal 2: {i}\n")
    sleep(0.1)

t1.print("This is Terminal 1\n")
t2.print("This is Terminal 2\n")
print("This is the main terminal")
print("Exiting in 10 seconds")
sleep(10)
quit()