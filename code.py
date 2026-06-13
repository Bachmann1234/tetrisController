"""
code.py — Main loop for the Tetris split controller (keyboard mode).

Hardware: Raspberry Pi Pico running CircuitPython.
Wiring:  All 8 buttons direct-wired, SW+ to GPIO, SW- to GND.
         Internal pull-ups enabled — LOW = pressed.
         Left-half buttons arrive via GX16-8 cable but are
         electrically identical from the Pico's perspective.

Button-to-key map (matches TETR.IO / Tetris Effect defaults):
  GP2 = Soft Drop      → Down Arrow
  GP3 = Right          → Right Arrow
  GP4 = Left           → Left Arrow
  GP5 = Hard Drop      → Space
  GP6 = Rotate CCW     → Z
  GP7 = Rotate CW      → X
  GP8 = Hold           → C
  GP9 = Zone / Start   → A
"""

import board
import digitalio
import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# ---------- keyboard HID device ----------

kbd = Keyboard(usb_hid.devices)

# ---------- button definitions ----------

# (GPIO pin, keycode)
BUTTONS = (
    (board.GP2, Keycode.DOWN_ARROW),   # Soft Drop
    (board.GP3, Keycode.RIGHT_ARROW),  # Right
    (board.GP4, Keycode.LEFT_ARROW),   # Left
    (board.GP5, Keycode.SPACE),        # Hard Drop
    (board.GP6, Keycode.Z),            # Rotate CCW
    (board.GP7, Keycode.X),            # Rotate CW
    (board.GP8, Keycode.C),            # Hold
    (board.GP9, Keycode.A),            # Zone / Start
)

DEBOUNCE_SECS = 0.010  # 10 ms debounce

# ---------- set up GPIO inputs with pull-ups ----------

buttons = []
for pin, keycode in BUTTONS:
    dio = digitalio.DigitalInOut(pin)
    dio.direction = digitalio.Direction.INPUT
    dio.pull = digitalio.Pull.UP
    buttons.append((dio, keycode))

# ---------- debounce state ----------
# For each button: [stable_pressed, last_raw, last_change_time]
debounce = [
    [False, False, 0.0]
    for _ in buttons
]

# ---------- main loop ----------

while True:
    now = time.monotonic()

    for i, (dio, keycode) in enumerate(buttons):
        raw_pressed = not dio.value  # LOW = pressed (pull-up)
        state = debounce[i]

        if raw_pressed != state[1]:        # raw state changed
            state[1] = raw_pressed
            state[2] = now                 # reset timer

        if now - state[2] >= DEBOUNCE_SECS:
            if state[1] != state[0]:       # stable state changed
                state[0] = state[1]
                if state[0]:
                    kbd.press(keycode)
                else:
                    kbd.release(keycode)
