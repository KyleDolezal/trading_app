from getkey import getkey
from sys import exit

def handle_exit():
    key_pressed = getkey(blocking=False)
    if key_pressed == "q":
        print("Goodbye")
        exit()