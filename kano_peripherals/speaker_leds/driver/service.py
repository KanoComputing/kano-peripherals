# service.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Low level programming of the LED Speaker chip through a DBus Service.
# Calls to the API (set_led* methods) are serialised to address OS concurency.
#
# Using the high_level functions from multiple processes will MERGE animations!
# It was thought that Kano apps using it would use lock() to get exclusive access.
# The locking mechanism is a binary semaphore with priority levels and REQUIRES one to
# unlock() it afterwards.
# However, there is a safety mechanism in place in case that fails.


import os
import math
import dbus
import dbus.service
from smbus import SMBus

from gi.repository import GObject

from kano.logging import logger
from kano.utils import run_cmd

from kano_peripherals.priority_lock import PriorityLock
from kano_peripherals.speaker_leds.driver.pwm_driver import PWM
from kano_peripherals.paths import BUS_NAME, SPEAKER_LEDS_OBJECT_PATH, SPEAKER_LEDS_IFACE


class SpeakerLEDsService(dbus.service.Object):
    """
    This is a DBus Service provided by kano-boards-daemon.

    It exports an object to /me/kano/boards/SpeakerLED and
    its interface to me.kano.boards.SpeakerLED

    Does not require sudo.
    """

    # LED Speaker Hardware Spec - Addresses of PCA9685 on bus
    # NOTE: most of these should not be exported to apps
    CHIP0_ADDR = 0x40
    LED_REG_BASE = 0x6
    NUM_LEDS = 10            # this is public
    LEDS_PER_CHIP = 5
    COLOURS_PER_LED = 3
    SPEAKER_LED_GAMMA = 0.5

    # polling rates of the threads used in the service
    DETECT_THREAD_POLL_RATE = 1000 * 5      # ms TODO: how big should this be?
    LOCKING_THREAD_POLL_RATE = 1000 * 10    # ms TODO: how big should this be?

    def __init__(self):
        name = dbus.service.BusName(BUS_NAME, bus=dbus.SystemBus())
        dbus.service.Object.__init__(self, name, SPEAKER_LEDS_OBJECT_PATH)

        self.is_plugged = False      # flag for GPIO plugged / unplugged LED Speaker
        self.locks = PriorityLock()  # locking with priority levels for exclusive access

        GObject.threads_init()
        GObject.timeout_add(self.DETECT_THREAD_POLL_RATE, self._detect_thread)

        self._init_i2cbus()
        if not self.i2cbus:
            logger.error('LED Speaker - Failed to load I2C kernel module')

    def _detect_thread(self):
        """
        Detect if the LED Speaker is plugged in.
        This method is run in a separate thread with GObject.

        It handles 2 events: onPlugged and onUnplugged. We setup the chip when
        detected for it to become usable. On these events it also starts/stops
        the cpu-monitor animation.
        """
        detected = self.detect()

        # we just detected the LED Speaker being plugged in
        if detected and not self.is_plugged:  # TODO: emit a signal here?
            self.setup(False)
            self.set_leds_off()  # TODO: emit a signal here to do an anim instead?

        # we just detected the LED Speaker was unplugged
        # if not detected and self.is_plugged:  # TODO: emit a signal here?
        #     pass

        self.is_plugged = detected

        return True  # keep calling this method indefinitely

    def _locking_thread(self):
        """
        Check if the locking processes are still alive.
        This method is run in a separate thread with GObject.

        If any process that locked the API has died, it automatically unlocks
        its priority level. It keeps executing as long as there are locks.
        """

        for priority in xrange(len(self.locks)):
            lock_data = self.locks.get(priority)

            if lock_data is not None:
                try:
                    os.kill(lock_data['PID'], 0)

                except OSError:
                    # the current locking process has died
                    logger.warn('[{}] with PID [{}]  and priority [{}] died and forgot'
                                '  to unlock the LED Speaker API. Unlocking.'
                                .format(lock_data['cmd'], lock_data['PID'], priority))
                    self.locks.remove_priority(priority)

                except Exception as e:
                    logger.warn('Something unexpected occurred in _locking_thread'
                                ' - [{}]'.format(e))

        # while there are still locks active, keep calling this function indefinitely
        return not self.locks.is_empty()

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

        Returns:
            True or False if the LED Speaker was detected.
        """
        try:
            if not self.i2cbus:
                self._init_i2cbus()

            if self.i2cbus:
                self.i2cbus.write_quick(self.CHIP0_ADDR)
                self.i2cbus.write_quick(self.CHIP0_ADDR + 1)
                return True
            else:
                # could not initialise the i2cbus
                return False

        except IOError:
            # the LED Speaker is not plugged in
            return False
        except Exception as e:
            logger.error('LED Speaker - Something unexpected occurred in detect - [{}]'
                         .format(e))

    @dbus.service.method(SPEAKER_LEDS_IFACE, in_signature='b', out_signature='')
    def setup(self, check):
        """
        Setup the LED Speaker chip for it to become usable.

        Args:
            check - boolean to enable chip mode check
        """

        if not self.detect():
            logger.warn('LED Speaker Board was not detected!')
            return

        p0 = PWM(self.i2cbus, self.CHIP0_ADDR)
        p1 = PWM(self.i2cbus, self.CHIP0_ADDR + 1)

        if not (check or p0.check()):
            p0.reset()
            p0.setPWMFreq(60)  # Set frequency to 60 Hz

        if not (check or p1.check()):
            p1.reset()
            p1.setPWMFreq(60)  # Set frequency to 60 Hz

    @dbus.service.method(SPEAKER_LEDS_IFACE, in_signature='i', out_signature='b',
                         sender_keyword='sender_id')
    def lock(self, priority, sender_id=None):
        """
        Block all other API calls with a lower priority.

        By calling this method, all other processes with a lower priority and a
        different sender_id (unique bus name) using the API will be locked out.
        USE WITH CAUTION!

        By default it is used by the OS with priority levels 1 and 2.
        All other apps are free to lock the API with a higher priority.

        It has a safety mechanism that starts a thread to check if the locking
        process is still alive. So please only call it once per app!

        Args:
            priority - number representing the priority level (default is 1 to 10).

        Returns:
            True or False if the operation was successful.
        """
        successful = False

        if self.locks.get(priority) is None and sender_id:
            lock_data = self._get_sender_data(sender_id)

            if self.locks.is_empty():
                GObject.timeout_add(self.LOCKING_THREAD_POLL_RATE, self._locking_thread)

            self.locks.put(priority, lock_data)
            successful = True

            logger.info('LED Speaker locked by [{}] with PID [{}] and priority [{}]'
                        .format(lock_data['cmd'], lock_data['PID'], priority))

        return successful

    @dbus.service.method(SPEAKER_LEDS_IFACE, in_signature='', out_signature='b',
                         sender_keyword='sender_id')
    def unlock(self, sender_id=None):
        """
        Unlock the API from the calling sender.

        The lock with a given priority level specific to the sender_id is removed.
        It does not unlock for other processes nor does it guarantee that the API
        is fully unlocked afterwards.

        IT IS IMPERATIVE to call this method after locking the API when your app
        finishes. Please do not rely on the _locking_thread to do this for you!

        Returns:
            True or False if the operation was successful.
        """
        successful = False

        if sender_id:
            lock_data = self._get_sender_data(sender_id)
            successful = self.locks.remove(lock_data)

            if successful:
                logger.info('LED Speaker unlocked from [{}] with PID [{}]'
                            .format(lock_data['cmd'], lock_data['PID']))

        return successful

    @dbus.service.method(SPEAKER_LEDS_IFACE, in_signature='i', out_signature='b')
    def is_locked(self, priority):
        """
        Check if the given priority level or any above are locked.

        Args:
            priority - number representing the priority level (default is 1 to 10).

        Returns:
            True or False if the API is locked on the given priority level.
        """
        return self.locks.contains_above(priority)

    @dbus.service.method(SPEAKER_LEDS_IFACE, in_signature='', out_signature='b',
                         sender_keyword='sender_id')
    def set_leds_off(self, sender_id=None):
        """
        Set all LEDs off.
        This method can be locked by other processes.

        Returns:
            True or False if the operation was successful.
        """
        if self.locks.get() and sender_id and \
           self.locks.get()['sender_id'] != sender_id:
                return False

        return self.set_all_leds([(0, 0, 0)] * self.NUM_LEDS)

    @dbus.service.method(SPEAKER_LEDS_IFACE, in_signature='a(ddd)', out_signature='b',
                         sender_keyword='sender_id')
    def set_all_leds(self, values, sender_id=None):
        """
        Set all LED values.
        This method can be locked by other processes.

        Args:
            values - list of (r,g,b) tuples where r,g,b are between 0.0 and 1.0

        Returns:
            True or False if the operation was successful.
        """
        if self.locks.get() and sender_id and \
           self.locks.get()['sender_id'] != sender_id:
                return False

        # TODO: there is potential for more efficiency because we
        # can transfer 32 bytes at a time over the i2c bus
        for idx, val in enumerate(values[:self.NUM_LEDS]):
            successful = self.set_led(idx, val)
            if not successful:
                return False

        return True

    @dbus.service.method(SPEAKER_LEDS_IFACE, in_signature='i(ddd)', out_signature='b',
                         sender_keyword='sender_id')
    def set_led(self, num, rgb, sender_id=None):
        """
        Set an LED value.
        This method can be locked by other processes.

        Args:
            num - LED index on the board
            rgb - and (r,g,b) tuple where r,g,b are between 0.0 and 1.0

        Returns:
            True or False if the operation was successful.
        """
        if self.locks.get() and sender_id and \
           self.locks.get()['sender_id'] != sender_id:
                return False

        addr = self.CHIP0_ADDR + (num / self.LEDS_PER_CHIP)
        num = num % self.LEDS_PER_CHIP

        base = num * self.COLOURS_PER_LED * 4  # 4 registers per PWM

        dat = []
        for idx, val in enumerate(rgb):
            dat.extend(self._convert_val_to_pwm(val, 0))

        reg = self.LED_REG_BASE + base

        try:
            self.i2cbus.write_i2c_block_data(addr, reg, dat)
        except IOError:
            # occurs when an animation is running and the user unplugs the LED Speaker
            # TODO: emit a signal here?
            return False
        except AttributeError:
            # occurs when the i2cmodule was not initialised
            return False
        except Exception as e:
            logger.error('LED Speaker - Something unexpected occurred in set_led - [{}]'
                         .format(e))
            return False

        return True

    @dbus.service.method(SPEAKER_LEDS_IFACE, in_signature='', out_signature='i')
    def get_num_leds(self):
        """
        Get the number of LEDs the LED Speaker has.

        Returns:
            NUM_LEDS - integer number of LEDs
        """
        return self.NUM_LEDS

    def _get_sender_data(self, sender_id):
        """
        Get sender_id, cmd, and PID from the API caller.
        """
        pid = self._get_sender_pid(sender_id)
        cmd = self._get_sender_cmd(pid)

        lock_data = {
            'sender_id': sender_id,
            'PID': pid,
            'cmd': cmd
        }
        return lock_data

    def _get_sender_pid(self, sender_id):
        """
        Get the PID of the process with the sender_id unique bus name.
        """
        sender_pid = None

        if sender_id:
            dbi = dbus.Interface(
                dbus.SystemBus().get_object('org.freedesktop.DBus', '/'),
                'org.freedesktop.DBus'
            )
            sender_pid = dbi.GetConnectionUnixProcessID(sender_id)

        return sender_pid

    def _get_sender_cmd(self, sender_pid):
        """
        Get the process name of a given PID. Used for logging (and blaming).
        """
        cmd = 'ps -p {} -o cmd='.format(sender_pid)
        output, _, _ = run_cmd(cmd)
        return output.strip()

    def _init_i2cbus(self):
        self.i2cbus = SMBus(1)  # Everything except early 256MB pi'

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
