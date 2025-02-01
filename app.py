from getkey import getkey
from sys import exit

print("Welcome to the trading app. Hit \'q\' to quit.")

while True:
    key_pressed = getkey(blocking=False)
    if key_pressed == "q":
        print("Goodbye")
        exit()
    pass