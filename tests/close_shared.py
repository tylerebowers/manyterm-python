# run this after there is a shared terminal open to close it.

from manyterm import SharedTerminal
from time import sleep
import uuid

print("Closing the shared terminal.")

# the shared terminal
st = SharedTerminal(uid="a_unique_id")

# something unique to this instance to print
st.close()