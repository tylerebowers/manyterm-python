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

#close the terminals (this is not necessary if the program is to be terminated)
print("Closing terminals in 5 seconds")
sleep(5)
t1.close()
t2.close()

print("Exiting in 5 seconds")
sleep(5)
quit()