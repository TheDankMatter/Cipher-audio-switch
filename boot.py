import storage
import board
from app.button import Button

button = Button(board.IO3)

# Disable mass storage if button is not pressed.
button.update()
if button.value:
   storage.disable_usb_drive()