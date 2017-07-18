# speaker_led.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# High level driver for the LED Speaker peripheral. This acts as an
# LED programming library.


import math
import traceback
from smbus import SMBus

from kano.logging import logger

from kano_peripherals.speaker_leds.driver.pwm_driver import PWM


class SpeakerLed(object):
    """
    High level driver for the LED Speaker peripheral.

    Does not require sudo, requires I2C kernel module to be loaded.
    """

    # LED Speaker Hardware Spec - Addresses of PCA9685 on bus
    # NOTE: most of these should not be exported to apps
    CHIP0_ADDR = 0x40
    LED_REG_BASE = 0x6
    NUM_LEDS = 10
    LEDS_PER_CHIP = 5
    COLOURS_PER_LED = 3
    SPEAKER_LED_GAMMA = 0.5

    def __init__(self):
        """
        Constructor for the SpeakerLed.
        """
        super(SpeakerLed, self).__init__()

        # Initialisation flags.
        self.is_initialised = False
        self.is_setup = False

        # The I2C bus used to read and write on the GPIO pins.
        self.i2cbus = None

    def initialise(self):
        """
        Initialisation of the driver.

        Returns:
            successful - bool whether or not the operation was successful
        """
        if self.is_initialised:
            return True

        try:
            self.i2cbus = SMBus(1)  # Everything except early 256MB pi
        except:
            logger.error(
                'SpeakerLed: initialise: Caught unexpected error initialising the i2c'
                ' bus:\n{}'.format(traceback.format_exc())
            )
            return False

        self.is_initialised = True
        return True

    def is_connected(self, with_setup=True):
        """
        There is no defined way to detect what kind of peripheral is on an i2c bus.
        So we have to try reading and writing it. Worse, according to:
        https://github.com/groeck/i2c-tools/blob/master/tools/i2cdetect.c
        a read corrupts some chips and a write corrupts others.

        We know that the speaker LED board has chips present at address 0x40 and 0x41,
        so test both of these and assume it is present if both respond. We use
        'quick write' which seems to leave the chip in the same state.

        Returns:
            True or False if the LED Speaker was detected.
        """
        if not self.is_initialised:
            logger.error('SpeakerLed: is_connected: The board was not initialised previously!')
            if not self.initialise():
                return False

        try:
            self.i2cbus.write_quick(self.CHIP0_ADDR)
            self.i2cbus.write_quick(self.CHIP0_ADDR + 1)

        except IOError:
            # the LED Speaker is not plugged in
            return False
        except:
            logger.error(
                'SpeakerLed: is_connected: Something unexpected occurred in detect:\n{}'
                ''.format(traceback.format_exc())
            )
            return False

        if with_setup:
            return self._setup()
        else:
            return True

    def _setup(self):
        """
        Setup the LED Speaker chips for it to become usable (set the LEDs).

        Returns:
            successful - bool whether or not the operation was successful
        """
        if self.is_setup:
            return True

        try:
            p0 = PWM(self.i2cbus, self.CHIP0_ADDR)
            p1 = PWM(self.i2cbus, self.CHIP0_ADDR + 1)

            if not p0.check():
                p0.reset()
                p0.setPWMFreq(60)  # Set frequency to 60 Hz

            if not p1.check():
                p1.reset()
                p1.setPWMFreq(60)  # Set frequency to 60 Hz

        except IOError:
            # the LED Speaker is not plugged in
            return False
        except:
            logger.error(
                'SpeakerLed: _setup: Caught unexpected error configuring the chips:\n{}'
                ''.format(traceback.format_exc())
            )
            return False

        self.is_setup = True
        return True

    def set_led(self, led_idx, rgb):
        """
        Set the colour output on a specified LED.

        Args:
            led_idx - int led index from 0 to NUM_LEDS - 1
            rgb     - tuple of int red, green, blue intensity from 0.0 to 1.0

        Returns:
            successful - bool whether or not the operation was successful
        """
        addr = self.CHIP0_ADDR + (led_idx / self.LEDS_PER_CHIP)
        led_idx = led_idx % self.LEDS_PER_CHIP

        base = led_idx * self.COLOURS_PER_LED * 4  # 4 registers per PWM

        dat = []
        for idx, val in enumerate(rgb):
            dat.extend(self._convert_val_to_pwm(val, 0))

        reg = self.LED_REG_BASE + base

        try:
            self.i2cbus.write_i2c_block_data(addr, reg, dat)
        except IOError:
            # Occurs when an animation is running and the user unplugs the Speaker LED.
            return False
        except AttributeError:
            # Occurs when the i2cmodule was not initialised.
            return False
        except:
            logger.error(
                'SpeakerLed: _setup: Caught unexpected error when writing on the i2c:\n{}'
                ''.format(traceback.format_exc())
            )
            return False

        return True

    # --- Private Helpers ---------------------------------------------------------------

    def _convert_val_to_pwm(self, val, num):
        """
        Convert an intensity value to a PCA9685 PWM on/off register settings.
        """
        phase = num * 4096 / 32

        val = max(val, 0.0001)
        val = min(val, 1.0)

        val = self._linearize(val, 4096, self.SPEAKER_LED_GAMMA)

        if val == 0:
            # all off needs a special value: set bit 12
            on = 0x1000
            off = 0
        else:
            on = phase & 0xfff
            off = int((4096 - val + phase) & 0xfff)

        return (on & 0xff, on >> 8, off & 0xff, off >> 8)

    def _linearize(self, val, steps, gamma):
        return int(math.pow(steps, math.pow(val, gamma))) - 1
