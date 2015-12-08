# service.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Low level programming of the LED chip. Also includes linerarity adjustment.
# Setup of the chip uses pwm_driver.py, but led programming does not go
# via that file to avoid overhead.


import os
import time
import math
import dbus
import dbus.service
from smbus import SMBus

from gi.repository import GObject

from kano_peripherals.speaker_leds.driver.pwm_driver import PWM
from kano_peripherals.paths import BUS_NAME, SPEAKER_LEDS_OBJECT_PATH, SPEAKER_LEDS_IFACE


class SpeakerLEDsService(dbus.service.Object):
    """
    TODO: description
    """

    # LED Speaker Hardware Spec - Addresses of PCA9685 on bus
    # NOTE: most of these should not be exported to apps
    CHIP0_ADDR = 0x40
    LED_REG_BASE = 0x6
    QUANTIZE = False         # this is public
    NUM_LEDS = 10            # this is public
    LEDS_PER_CHIP = 5
    COLOURS_PER_LED = 3
    SPEAKER_LED_GAMMA = 0.5

    #
    DETECT_THREAD_POLL_RATE = 1000 * 2  # ms TODO: how big should this be?

    def __init__(self):
        name = dbus.service.BusName(BUS_NAME, bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, name, SPEAKER_LEDS_OBJECT_PATH)

        self.is_plugged = False

        GObject.threads_init()
        GObject.timeout_add(self.DETECT_THREAD_POLL_RATE, self._detect_thread)

        self._init_i2cbus()

    def _init_i2cbus(self):
        module_loaded = os.system('modprobe i2c_dev') == 0
        if not module_loaded:
            self._logger().error('failed to load I2C kernel module')
            self.i2cbus = None
        else:
            self.i2cbus = SMBus(1)  # Everything except early 256MB pi'

    def _detect_thread(self):
        """
        """
        detected = self.detect()

        # we just detected the LED Speaker being plugged in
        if detected and not self.is_plugged:
            time.sleep(0.005)    # TODO: do I need this here?
            self.setup(False)
            self.set_leds_off()  # TODO: emit a signal here to do an anim instead?

        self.is_plugged = detected

        return True  # keep calling this method indefinitely

    @dbus.service.method(SPEAKER_LEDS_IFACE, in_signature='', out_signature='b')
    def detect(self):
        """
        There is no defined way to detect what kind of peripheral is on an i2c bus.
        So we have to try reading and writing it.
        Worse, according to:
        https://github.com/groeck/i2c-tools/blob/master/tools/i2cdetect.c
        a read corrupts some chips and a write corrupts others.

        We know that the speaker LED board has chips present at address
        0x40 and 0x41, so test both of these and assume it is present if
        both respond.
        We use 'quick write' which seems to leave the chip in the same state.
        """
        try:
            self.i2cbus.write_quick(self.CHIP0_ADDR)
            self.i2cbus.write_quick(self.CHIP0_ADDR + 1)
            return True
        except IOError:
            return False

    @dbus.service.method(SPEAKER_LEDS_IFACE, in_signature='b', out_signature='')
    def setup(self, check):
        """
        TODO: description
        """

        if not self.detect():
            # raise NotDetected
            self._logger().warn('LED Speaker Board was not detected!')
            return

        p0 = PWM(self.i2cbus, self.CHIP0_ADDR)
        p1 = PWM(self.i2cbus, self.CHIP0_ADDR + 1)

        if not (check or p0.check()):
            p0.reset()
            p0.setPWMFreq(60)  # Set frequency to 60 Hz

        if not (check or p1.check()):
            p1.reset()
            p1.setPWMFreq(60)  # Set frequency to 60 Hz

    @dbus.service.method(SPEAKER_LEDS_IFACE, in_signature='', out_signature='')
    def set_leds_off(self):
        """
        NB, could power down the PWM here
        """
        self.set_all_leds([(0, 0, 0)] * self.NUM_LEDS)

    @dbus.service.method(SPEAKER_LEDS_IFACE, in_signature='a(ddd)', out_signature='')
    def set_all_leds(self, values):
        """
        Set all LED values. Note that there is potential for more efficiency
        because we can transfer 32 bytes at a time over the i2c bus
        """

        for idx, val in enumerate(values[:self.NUM_LEDS]):
            self.set_led(idx, val)

    @dbus.service.method(SPEAKER_LEDS_IFACE, in_signature='i(ddd)', out_signature='')
    def set_led(self, num, rgb):
        """
        TODO: description
        """

        addr = self.CHIP0_ADDR + (num / self.LEDS_PER_CHIP)
        num = num % self.LEDS_PER_CHIP

        base = num * self.COLOURS_PER_LED * 4  # 4 registers per PWM

        dat = []
        for idx, val in enumerate(rgb):
            # dat.extend(convertValToPWM(val, num+idx))
            dat.extend(self._convert_val_to_pwm(val, 0))

        reg = self.LED_REG_BASE + base
        #  print addr,hex(reg),map(hex,dat)

        try:
            self.i2cbus.write_i2c_block_data(addr, reg, dat)
        except:
            # occurs when an animation is running and the user unplugs the LED Speaker
            pass  # TODO: emit a signal here?

    @dbus.service.method(SPEAKER_LEDS_IFACE, in_signature='', out_signature='a{sv}')
    def get_data(self):
        """
        TODO: description
        NOTE: The out_signature here indicates the return type as being a
              dictionary with String keys and Variant values (multiple types).
        """
        return {
            'NUM_LEDS': self.NUM_LEDS,
            'QUANTIZE': self.QUANTIZE
        }

    def _convert_val_to_pwm(self, val, num):
        """
        Convert an intensity value to a PCA9685 PWM on/off register settings.
        """

        phase = num * 4096 / 32

        val = max(val, 0.0001)
        val = min(val, 1.0)

        if self.QUANTIZE:
            val = int(val * 4095) & 0x1e00
        else:
            val = self._linearize(val, 4096, self.SPEAKER_LED_GAMMA)

        if val == 0:
            # all off needs a special value: set bit 12
            on = 0x1000
            off = 0
        else:
            on = phase & 0xfff
            off = int((4096 - val + phase) & 0xfff)

        # print hex(on), hex(off)

        return (on & 0xff, on >> 8, off & 0xff, off >> 8)

    def _linearize(self, val, steps, gamma):
        return int(math.pow(steps, math.pow(val, gamma))) - 1

    def _logger():
        # lazy load logging to avoid 1 second startup time
        import kano.logging
        return kano.logging.logger
