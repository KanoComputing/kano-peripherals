# service.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Low level programming of the LED Speaker chip through a DBus Service.
# Calls to the API (set_led_* methods) are serialised to address OS concurency.
#
# Using the high_level functions from multiple processes will MERGE animations!
# It was thought that Kano apps using it would use lock() to get exclusive access.
# The locking mechanism is a binary semaphore with priority levels and REQUIRES one to
# unlock() it afterwards.
# However, there is a safety mechanism in place in case that fails.


import dbus
import dbus.service

from kano.logging import logger

from kano_peripherals.base_device_service import BaseDeviceService
from kano_peripherals.lockable_service import LockableService
from kano_peripherals.speaker_leds.speaker_led import SpeakerLed
from kano_peripherals.paths import SPEAKER_LEDS_OBJECT_PATH, SERVICE_API_IFACE


class SpeakerLEDsService(BaseDeviceService):
    """
    This is a DBus Service provided by kano-boards-daemon.

    It exports an object to /me/kano/boards/SpeakerLED and
    its interface to me.kano.boards.SpeakerLED

    Does not require sudo.
    """

    # The number of LEDs on the PiHat ring. This value has a getter.
    NUM_LEDS = SpeakerLed.NUM_LEDS

    # The poll rate for checking if the board is still plugged in.
    DETECT_THREAD_POLL_RATE = 5 * 1000  # milliseconds

    # The top priority level for an API lock. This value has a getter.
    MAX_PRIORITY_LEVEL = 10

    def __init__(self, bus_name):
        """
        Constructor for the SpeakerLEDsService.

        Given that services should be ready to use when they come online, it also
        performs initialisation and starts subprocesses. It also emits the
        'device_connected' DBus signal as the service is expected to be brought
        up only when the device was discovered.

        Args:
            bus_name - A dbus.service.BusName object to configure the base address.
        """
        super(SpeakerLEDsService, self).__init__(bus_name, SPEAKER_LEDS_OBJECT_PATH)

        # The high level 'library' object controlling the hardware.
        self.speaker_led = SpeakerLed()
        self.speaker_led.initialise()

        # Locking with priority levels for exclusive access.
        self.lockable_service = LockableService(max_priority=self.MAX_PRIORITY_LEVEL)

        # Lazy import to avoid issue of importing from this module externally.
        from gi.repository import GObject

        # Start the detection polling routine.
        GObject.threads_init()
        self.detect_thread_id = GObject.timeout_add(
            self.DETECT_THREAD_POLL_RATE, self._detect_thread
        )

        # The first time we detect the device we must turn off the LEDs, because they
        # have been manufactured (not designed!) with the LEDs ON by default...
        self.speaker_led._setup()
        self.set_leds_off()

        self.device_connected(self.get_object_path())

    def clean_up(self):
        """
        Stop all running (sub)processes and clean up before process termination.
        """

        # Lazy import to avoid issue of importing from this module externally.
        from gi.repository import GObject

        GObject.source_remove(self.detect_thread_id)

        if not self.set_leds_off():
            logger.error('SpeakerLEDsService: stop: Could not turn off leds!')

    # --- Board Detection ---------------------------------------------------------------

    @staticmethod
    def quick_detect():
        """
        A device detection static method complete with library initialisation.
        Inherited and implemented from BaseDeviceService (look there for more info).

        Returns:
            connected - bool whether or not the device is plugged in
        """

        # TODO: Check if the service is online, if true, return true and log an error.

        speaker_led = SpeakerLed()

        if not speaker_led.initialise():
            return False

        return speaker_led.is_connected(with_setup=False)

    @dbus.service.method(SERVICE_API_IFACE, in_signature='', out_signature='b')
    def detect(self):
        """
        Detect whether the LED Speaker board is connected.

        Returns:
            connected - bool whether the board is plugged in or not.
        """
        return self.speaker_led.is_connected()

    @dbus.service.method(SERVICE_API_IFACE, in_signature='', out_signature='b')
    def is_plugged(self):
        """
        TODO: Same as detect, remove.
        """
        return self.speaker_led.is_connected()

    def _detect_thread(self):
        """
        Poll the detection for LED Speaker to know when it is unplugged.

        When the LED Speaker is unplugged, the 'device_disconnected' DBus signal is
        emitted. This method is run in a separate thread with GObject.
        """
        detected = self.detect()

        if not detected:
            self.device_disconnected(self.get_object_path())

        # Keep calling this method indefinitely.
        return True

    # --- API Locking -------------------------------------------------------------------

    @dbus.service.method(SERVICE_API_IFACE, in_signature='i', out_signature='s',
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
            token - str with an API token for identification or empty str if unsuccessful
        """
        return self.lockable_service.lock(priority, sender_id)

    @dbus.service.method(SERVICE_API_IFACE, in_signature='', out_signature='b',
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
        return self.lockable_service.unlock(sender_id)

    @dbus.service.method(SERVICE_API_IFACE, in_signature='i', out_signature='b')
    def is_locked(self, priority):
        """
        Check if the given priority level or any above are locked.

        Args:
            priority - number representing the priority level (default is 1 to 10).

        Returns:
            True or False if the API is locked on the given priority level.
        """
        return self.lockable_service.is_locked(priority)

    @dbus.service.method(SERVICE_API_IFACE, in_signature='', out_signature='i')
    def get_max_lock_priority(self):
        """
        Get the maximum priority level to lock with.

        Returns:
            MAX_PRIORITY_LEVEL - unsigned integer number of priority levels
        """
        return self.lockable_service.get_max_lock_priority()

    # --- LED Programming with Locked API -----------------------------------------------

    @dbus.service.method(SERVICE_API_IFACE, in_signature='s', out_signature='b',
                         sender_keyword='sender_id')
    def set_leds_off_with_token(self, token, sender_id=None):
        """
        Set all LEDs off.
        This method can be used in multiprocess contexts when the parent
        passes the lock token to its children.

        Args:
            token - string returned by lock() used to bypass the top lock.

        Returns:
            True or False if the operation was successful.
        """
        if sender_id and \
           self.lockable_service.get_lock().get() and \
           self.lockable_service.get_lock().get()['sender_id'] != token:
            return False

        return self.set_leds_off(sender_id=token)

    @dbus.service.method(SERVICE_API_IFACE, in_signature='a(ddd)s', out_signature='b',
                         sender_keyword='sender_id')
    def set_all_leds_with_token(self, values, token, sender_id=None):
        """
        Set all LED values.
        This method can be used in multiprocess contexts when the parent
        passes the lock token to its children.

        Args:
            values - list of (r,g,b) tuples where r,g,b are between 0.0 and 1.0
            token - string returned by lock() used to bypass the top lock.

        Returns:
            True or False if the operation was successful.
        """
        if sender_id and \
           self.lockable_service.get_lock().get() and \
           self.lockable_service.get_lock().get()['sender_id'] != token:
            return False

        return self.set_all_leds(values, sender_id=token)

    @dbus.service.method(SERVICE_API_IFACE, in_signature='i(ddd)s', out_signature='b',
                         sender_keyword='sender_id')
    def set_led_with_token(self, num, rgb, token, sender_id=None):
        """
        This method can be used in multiprocess contexts when the parent
        passes the lock token to its children.

        Args:
            num - LED index on the board
            rgb - and (r,g,b) tuple where r,g,b are between 0.0 and 1.0
            token - string returned by lock() used to bypass the top lock.

        Returns:
            True or False if the operation was successful.
        """
        if sender_id and \
           self.lockable_service.get_lock().get() and \
           self.lockable_service.get_lock().get()['sender_id'] != token:
            return False

        return self.set_led(num, rgb, sender_id=token)

    # --- LED Programming API -----------------------------------------------------------

    @dbus.service.method(SERVICE_API_IFACE, in_signature='', out_signature='b',
                         sender_keyword='sender_id')
    def set_leds_off(self, sender_id=None):
        """
        Set all LEDs off.
        This method can be locked by other processes.

        Returns:
            True or False if the operation was successful.
        """
        if sender_id and \
           self.lockable_service.get_lock().get() and \
           self.lockable_service.get_lock().get()['sender_id'] != sender_id:
            return False

        return self.set_all_leds([(0, 0, 0)] * self.NUM_LEDS)

    @dbus.service.method(SERVICE_API_IFACE, in_signature='a(ddd)', out_signature='b',
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
        if self.lockable_service.get_lock().get() and sender_id and \
           self.lockable_service.get_lock().get()['sender_id'] != sender_id:
                return False

        # TODO: there is potential for more efficiency because we
        # can transfer 32 bytes at a time over the i2c bus
        for idx, val in enumerate(values[:self.NUM_LEDS]):
            successful = self.set_led(idx, val)
            if not successful:
                return False

        return True

    @dbus.service.method(SERVICE_API_IFACE, in_signature='i(ddd)', out_signature='b',
                         sender_keyword='sender_id')
    def set_led(self, led_idx, rgb, sender_id=None):
        """
        Set an LED value.
        This method can be locked by other processes.

        Args:
            led_idx - int led index from 0 to NUM_LEDS - 1
            rgb     - tuple of int red, green, blue intensity from 0.0 to 1.0

        Returns:
            True or False if the operation was successful.
        """
        if self.lockable_service.get_lock().get() and sender_id and \
           self.lockable_service.get_lock().get()['sender_id'] != sender_id:
                return False

        return self.speaker_led.set_led(led_idx, rgb)

    @dbus.service.method(SERVICE_API_IFACE, in_signature='', out_signature='i')
    def get_num_leds(self):
        """
        Get the number of LEDs the Speaker LED has.

        Returns:
            NUM_LEDS - integer number of LEDs
        """
        return self.NUM_LEDS
