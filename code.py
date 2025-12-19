import time

import board
import busio
import digitalio
import microcontroller

import adafruit_is31fl3741
from adafruit_is31fl3741.adafruit_rgbmatrixqt import Adafruit_RGBMatrixQT


# Cart detection pin, if IO_SD_CART is LOW
# then a cart (with or without an SD card) is inserted
IO_SD_CART = digitalio.DigitalInOut(board.GP26)
IO_SD_CART.direction = digitalio.Direction.INPUT
IO_SD_CART.pull = digitalio.Pull.UP

# SD detection pin, if IO_SD_CARD is LOW
# then a cart WITH an SD card is inserted
# (vs a cart which is missing it's SD card)
IO_SD_CARD = digitalio.DigitalInOut(board.GP27)
IO_SD_CARD.direction = digitalio.Direction.INPUT
IO_SD_CARD.pull = digitalio.Pull.UP

# So if IO_SD_CART is LOW and IO_SD_CARD is HIGH
# We know someone put in an empty cartridge without
# any SD card in it. We should surface this error.

# In theory IO_SD_LED should read the LED from the
# cart drive to allow us to proxy the flashing to
# our RGB matrix, but it seems to not work.
IO_SD_LED = digitalio.DigitalInOut(board.GP3)
IO_SD_LED.direction = digitalio.Direction.INPUT
IO_SD_LED.pull = digitalio.Pull.DOWN

IO_BUTTON_OUT = digitalio.DigitalInOut(board.GP7)
IO_BUTTON_IN = digitalio.DigitalInOut(board.GP8)

IO_POWER_SW = digitalio.DigitalInOut(board.GP20)
IO_POWER_SW.direction = digitalio.Direction.OUTPUT
IO_POWER_SW.value = True

IO_S0 = digitalio.DigitalInOut(board.GP18)
IO_S0.direction = digitalio.Direction.INPUT

IO_S3 = digitalio.DigitalInOut(board.GP19)
IO_S3.direction = digitalio.Direction.INPUT

IO_LED_BLUE = digitalio.DigitalInOut(board.GP25)
IO_LED_BLUE.direction = digitalio.Direction.OUTPUT

IO_BUTTON_IN.direction = digitalio.Direction.INPUT
IO_BUTTON_OUT.direction = digitalio.Direction.OUTPUT
IO_BUTTON_OUT.value = True

PIN_SDA = board.GP4
PIN_SCL = board.GP5

i2c_working = False
IO_LED_BLUE.value = True

try:
    i2c = busio.I2C(sda=PIN_SDA, scl=PIN_SCL)
    is31 = adafruit_is31fl3741.IS31FL3741(i2c)

    is31 = Adafruit_RGBMatrixQT(i2c, allocate=adafruit_is31fl3741.PREFER_BUFFER)
    is31.set_led_scaling(0xFF)
    is31.global_current = 0xFF
    is31.enable = True
    i2c_working = True
    print("i2c working!")
except:
    time.sleep(1)
    microcontroller.reset()
    print("i2c failing!")
    i2c_working=False
    
last_value = False

DEVICE_ON = (True, False)
DEVICE_SLEEP = (False, True)
DEVICE_OFF = (False, False)
        
last_state = None
state = None

def set_led(device_state):
    if not i2c_working:
        IO_LED_BLUE.value = True
        return

    for y in range(3, 9):
        for x in range(5, 13):
            is31.pixel(x, y, 0x000000)
    
    if device_state == DEVICE_SLEEP:
        is31.enable = True
        for y in range(3, 9):
            for x in range(12, 13):
                is31.pixel(x, y, 0x0000FF)
    if device_state == DEVICE_OFF:
        is31.enable = True
        for y in range(5, 7):
            for x in range(12, 13):
                is31.pixel(x, y, 0xFF0000)
    if device_state == DEVICE_ON:
        is31.enable = True
        for y in range(3, 9):
            for x in range(5, 13):
                is31.pixel(x, y, 0x0000FF)
    is31.show()

while True:
    io_s = (IO_S0.value, IO_S3.value)
    
    if io_s == DEVICE_ON:
        state = DEVICE_ON
    if io_s == DEVICE_SLEEP:
        state = DEVICE_SLEEP
    if io_s == DEVICE_OFF:
        state = DEVICE_OFF
            
    if last_state != state:
        last_state = state
        set_led(state)
        
    if IO_BUTTON_IN.value != last_value:
        last_value = IO_BUTTON_IN.value
        
        if last_value:
            time.sleep(0.3)
            if IO_BUTTON_IN.value == True:
                IO_POWER_SW.value = False
                time.sleep(1)
                IO_POWER_SW.value = True
            else:
                print("Power not held")



