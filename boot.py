"""
boot.py — USB HID keyboard for Tetris controller.

Runs once at boot before code.py. Enables the default keyboard HID device.
No custom descriptor needed — CircuitPython's built-in keyboard device works.
"""

import usb_hid

usb_hid.enable((usb_hid.Device.KEYBOARD,))
