import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse
from neopixel import NeoPixel
from os import urandom
from supervisor import ticks_ms

TICKS_PERIOD = const(1<<29)
BLINK_ON_INTERVAL = const(1000)
BLINK_OFF_INTERVAL = const(2000)
HID_INTERVAL = const(1000)
MOUSE_DELTA_MIN = const(10)
MOUSE_DELTA_MAX = const(20)

def blink():
    start_ms = ticks_ms()
    interval = BLINK_OFF_INTERVAL
    # Let GP0 be dummy in case LED or NEOPIXEL is not defined
    # Assuming GP0 is not wired into something
    led = digitalio.DigitalInOut(board.LED if hasattr(board, 'LED') else board.GP0)
    led.direction = digitalio.Direction.OUTPUT
    pixel = NeoPixel(board.NEOPIXEL if hasattr(board, 'NEOPIXEL') else board.GP0, 1)

    def main():
        nonlocal start_ms, interval, led, pixel

        # Smaller than time.monotonic() data
        if ticks_ms() - start_ms < interval:
            return

        if not led.value:
            pixel.fill((0, 50, 0))
            interval = BLINK_ON_INTERVAL
        else:
            pixel.fill((0, 0, 0))
            interval = BLINK_OFF_INTERVAL

        led.value = not led.value
        start_ms = (start_ms + interval) % TICKS_PERIOD

    return main

def hid():
    start_ms = ticks_ms()
    interval = HID_INTERVAL
    keyboard = Keyboard(usb_hid.devices)
    mouse = Mouse(usb_hid.devices)

    def main():
        nonlocal start_ms, interval, keyboard, mouse

        if ticks_ms() - start_ms < interval:
            return

        random = urandom(5)

        modifier = Keycode.ALT if random[0] % 2 else Keycode.COMMAND
        keyboard.send(modifier, Keycode.TAB)

        delta_x = random[1] % (1 + MOUSE_DELTA_MAX - MOUSE_DELTA_MIN) + MOUSE_DELTA_MIN
        delta_y = random[2] % (1 + MOUSE_DELTA_MAX - MOUSE_DELTA_MIN) + MOUSE_DELTA_MIN
        delta_x = delta_x if random[3] % 2 else -delta_x
        delta_y = delta_y if random[4] % 2 else -delta_y
        mouse.move(delta_x, delta_y)

        start_ms = (start_ms + interval) % TICKS_PERIOD

    return main

# Cannot add attr to functions so we do nested functions
# Overwriting since we only need once
blink = blink()
hid = hid()

while True:
    blink()
    hid()
