from manyterm import SharedTerminal
from time import sleep
import uuid

print("Start this program multiple times concurrently to see how it works.")

# the shared terminal
st = SharedTerminal(uid="a_unique_id")

# something unique to this instance to print
my_id = str(uuid.uuid4())[:3]
print(f"I am {my_id}")
while True:
    st.print(f"Hello from {my_id}")
    sleep(1)