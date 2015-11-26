# speaker_leds/low_level.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Low level programming of the LED chip. Also includes linerarity adjustment.
# Setup of the chip useds pwm_driver.py, but led programming does not go
# via that file to avoid overhead.


from smbus import SMBus
import time
import math
from pwm_driver import PWM
import os

# Bus number is 1 on RPI2.


# lazy load logging to avoid 1 second startup time
def logger():
    import kano.logging
    return kano.logging.logger


module_loaded = os.system('modprobe i2c_dev') == 0
if not module_loaded:
    logger().error('failed to load I2C kernel module')
    i2cbus = None
else:
    i2cbus = SMBus(1)  # Everything except early 256MB pi'

# Addresses of PCA9685 on bus:

CHIP0_ADDR = 0x40

QUANTIZE = False

NUM_LEDS = 10
LEDS_PER_CHIP = 5

COLORS_PER_LED = 3

LED_REG_BASE = 0x6

SPEAKER_LED_GAMMA = 0.5


def detect():
    """
    There is no defined way to detect what kind of peripheral is on an i2c bus.
    So we have to try reading and writing it.
    Worse, according to:
    https://github.com/groeck/i2c-tools/blob/master/tools/i2cdetect.c
    a read corrupts some chips and a write corrupts others.

    We know that the speaker LED board  has chips present at address
    0x40  and 0x41, so test both of these and assume it is present if
    both respond.
    We use 'quick write' which seems to leave the chip in the same state.


    """
    try:
        i2cbus.write_quick(CHIP0_ADDR)
        i2cbus.write_quick(CHIP0_ADDR+1)
        return True
    except IOError:
        return False

class NotDetected(Exception):
    pass

def setup(check=False):
    """
    """

    if not detect():
        raise NotDetected

    p0 = PWM(i2cbus, CHIP0_ADDR)
    p1 = PWM(i2cbus, CHIP0_ADDR+1)

    if not (check or p0.check()):
        p0.reset()
        p0.setPWMFreq(60)                        # Set frequency to 60 Hz

    if not (check or p1.check()):
        p1.reset()
        p1.setPWMFreq(60)                        # Set frequency to 60 Hz


def linearize(val, steps, gamma):
    return int(math.pow(steps, math.pow(val, gamma)))-1


def convertValToPWM(val, num):
    """
    Convert an intensity value to a PCA9685 PWM on/off register settings.


    """

    phase = num * 4096 / 32

    val = max(val, 0.0001)
    val = min(val, 1.0)

    if QUANTIZE:
        val = int(val * 4095) & 0x1e00
    else:
        val = linearize(val, 4096, SPEAKER_LED_GAMMA)

    if val == 0:
        # all off needs a special value: set bit 12
        on = 0x1000
        off = 0
    else:
        on = phase & 0xfff
        off = int((4096 - val + phase) & 0xfff)

    # print hex(on), hex(off)

    return (on & 0xff, on >> 8, off & 0xff, off >> 8)


def setLed(num, rgb):

    addr = CHIP0_ADDR+(num / LEDS_PER_CHIP)
    num = num % LEDS_PER_CHIP

    base = num * COLORS_PER_LED * 4 # 4 registers per PWM

    dat = []
    for idx, val in enumerate(rgb):

        # dat.extend(convertValToPWM(val, num+idx))
        dat.extend(convertValToPWM(val, 0))

    reg = LED_REG_BASE + base
    #  print addr,hex(reg),map(hex,dat)

    i2cbus.write_i2c_block_data(addr, reg, dat)


def setAllLeds(values):
    """
    Set all LED values. Note that there is potential for more efficiency
    because we can transfer 32 bytes at a time over the i2c bus
    """

    for idx, val in enumerate(values[:NUM_LEDS]):
        setLed(idx, val)

def setLedsOff():
    """
    NB, could power down the PWM here 
    """
    setAllLeds([(0, 0, 0)] * NUM_LEDS)

# Not for production:
def test1():
    time.sleep(1)
    rng = range(0, 1000, 10)+range(1000, 0, -10)
    while True:
        for r in rng:
            setAllLeds([(r/1000.0, 0, 0)] * NUM_LEDS)


def test2(led):
    rng = range(0, 1000, 10)+range(1000, 0, -10)
    while True:
        for r in rng:
            setAllLeds([(r/1000.0, 0, 0)] * NUM_LEDS)
