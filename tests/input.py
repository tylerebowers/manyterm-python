#python -m tests.input
import manyterm 
from time import sleep


#make new terminals
t1 = manyterm.Terminal()
t2 = manyterm.Terminal(title="Customized Title (t2)")
#sleep(5)

#use the new terminals
print("This is the main terminal")
t1.print("This is Terminal 1")
t2.print("This is Terminal 2")

# get input fr om terminal 1
t2.print("Look at terminal 1 for input.")
inp = t1.input("What is your name? ")
t2.print(f"Your name is {inp}")
t1.print(f"Printed on the other terminal")

sleep(5)