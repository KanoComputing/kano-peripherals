# service.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Low level programming of the Pi Hat board through a DBus Service.
#
# Using the high_level functions from multiple processes will MERGE animations! It was
# thought that Kano apps using it would use lock() to get exclusive access. The locking
# mechanism is a binary semaphore with priority levels and REQUIRES one to unlock() it
# afterwards. However, there is a safety mechanism in place in case that fails.


import time
import dbus
import dbus.service
from multiprocessing import Process, Value

from gi.repository import GObject

from kano.logging import logger
from kano.utils import run_bg

from kano_peripherals.base_device_service import BaseDeviceService
from kano_peripherals.lockable_service import LockableService
from kano_peripherals.paths import PI_HAT_OBJECT_PATH, SERVICE_API_IFACE
from kano_pi_hat.kano_hat_leds import KanoHatLeds
from kano_pi_hat.kano_hat import KanoHat


class PiHatService(BaseDeviceService):
    """
    This is a DBus Service provided by kano-boards-daemon.

    It exports an object to /me/kano/boards/PiHat and
    its interface to me.kano.boards.PiHat

    Requires sudo.
    """

    # The number of LEDs on the PiHat ring. This value has a getter.
    NUM_LEDS = KanoHatLeds.LED_COUNT

    # The top priority level for an API lock. This value has a getter.
    MAX_PRIORITY_LEVEL = 10

    # The poll rate for checking if the board is still plugged in.
    DETECT_THREAD_POLL_RATE = 5 * 1000  # milliseconds

    def __init__(self, bus_name, pi_hat):
        """
        Constructor for the PiHatService.

        Given that services should be ready to use when they come online, it also
        performs initialisation and starts subprocesses. It also emits the
        'device_connected' DBus signal as the service is expected to be brought
        up only when the device was discovered.

        Args:
            bus_name - A dbus.service.BusName object to configure the base address.
        """
        super(PiHatService, self).__init__(bus_name, PI_HAT_OBJECT_PATH)

        self.lockable_service = LockableService(max_priority=self.MAX_PRIORITY_LEVEL)

        # The high level 'library' object controlling the hardware.
        self.pi_hat = pi_hat
        self.pi_hat.initialise()

        self.is_power_button_enabled = Value('b', True)

        self.power_button_thread = Process(
            target=self._power_button_thread,
            args=(self.is_power_button_enabled,)
        )
        self.power_button_thread.start()

        # Start the detection polling routine.
        GObject.threads_init()
        self.detect_thread_id = GObject.timeout_add(
            self.DETECT_THREAD_POLL_RATE, self._detect_thread
        )

        self.device_connected(self.get_object_path())

    def clean_up(self):
        """
        Stop all running (sub)processes and clean up before process termination.
        """
        GObject.source_remove(self.detect_thread_id)
        self.power_button_thread.terminate()

        if not self.set_leds_off():
            logger.error('PiHatService: stop: Could not turn off leds!')

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

        pi_hat = KanoHat()

        if pi_hat.initialise():
            return False

        connected = pi_hat.is_connected()
        pi_hat.clean_up()

        return connected

    @dbus.service.method(SERVICE_API_IFACE, in_signature='', out_signature='b')
    def detect(self):
        """
        Detect whether the PiHat board is connected.

        Returns:
            connected - bool whether the board is plugged in or not.
        """
        return self.pi_hat.is_connected()

    @dbus.service.method(SERVICE_API_IFACE, in_signature='', out_signature='b')
    def is_plugged(self):
        """
        TODO: Same as detect, remove.
        """
        return self.pi_hat.is_connected()

    def _detect_thread(self):
        """
        Poll the detection for PiHat to know when it is unplugged.

        When the PiHat is unplugged, the 'device_disconnected' DBus signal is emitted.
        This method is run in a separate thread with GObject.

        TODO: The library for this board uses WiringPi which can do hardware interrupts.
              We could remove this polling thread by having the hardware notify us.
        """
        detected = self.detect()

        if not detected:
            self.device_disconnected(self.get_object_path())

        return detected

    # --- API Locking -------------------------------------------------------------------

    @dbus.service.method(SERVICE_API_IFACE, in_signature='i', out_signature='s', sender_keyword='sender_id')
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

    @dbus.service.method(SERVICE_API_IFACE, in_signature='', out_signature='b', sender_keyword='sender_id')
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

    @dbus.service.method(SERVICE_API_IFACE, in_signature='s', out_signature='b', sender_keyword='sender_id')
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

    @dbus.service.method(SERVICE_API_IFACE, in_signature='a(ddd)s', out_signature='b', sender_keyword='sender_id')
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

    @dbus.service.method(SERVICE_API_IFACE, in_signature='i(ddd)s', out_signature='b', sender_keyword='sender_id')
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

    @dbus.service.method(SERVICE_API_IFACE, in_signature='', out_signature='b', sender_keyword='sender_id')
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

    @dbus.service.method(SERVICE_API_IFACE, in_signature='a(ddd)', out_signature='b', sender_keyword='sender_id')
    def set_all_leds(self, values, sender_id=None):
        """
        Set all LED values.
        This method can be locked by other processes.

        Args:
            values - list of (r,g,b) tuples where r,g,b are between 0.0 and 1.0

        Returns:
            True or False if the operation was successful.
        """
        if sender_id and \
           self.lockable_service.get_lock().get() and \
           self.lockable_service.get_lock().get()['sender_id'] != sender_id:
            return False

        return self.pi_hat.set_all_leds(values)

    @dbus.service.method(SERVICE_API_IFACE, in_signature='i(ddd)', out_signature='b', sender_keyword='sender_id')
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

        if sender_id and \
           self.lockable_service.get_lock().get() and \
           self.lockable_service.get_lock().get()['sender_id'] != sender_id:
            return False

        return self.pi_hat.set_led(num, rgb)

    @dbus.service.method(SERVICE_API_IFACE, in_signature='', out_signature='i')
    def get_num_leds(self):
        """
        Get the number of LEDs the LED Speaker has.

        Returns:
            NUM_LEDS - integer number of LEDs
        """
        return self.NUM_LEDS

    # --- Power Button ------------------------------------------------------------------

    @dbus.service.method(SERVICE_API_IFACE, in_signature='', out_signature='b')
    def is_power_button_enabled(self):
        """
        Check if the power button was enabled to the Interrupt Service Routine.
        Currently, this callback pops up the shutdown menu.

        Returns:
            enabled - boolean whether the button ISR will be run
        """
        return self.is_power_button_enabled.value

    @dbus.service.method(SERVICE_API_IFACE, in_signature='b', out_signature='')
    def set_power_button_enabled(self, enabled):
        """
        Enable or disable the power button from performing
        and signaling any actions.

        Args:
            enabled - boolean whether the button should register presses or not
        """
        self.is_power_button_enabled.value = enabled

    @dbus.service.signal(SERVICE_API_IFACE, signature='')
    def power_button_pressed(self):
        pass

    def _power_button_thread(self, is_enabled):
        """
        Register the power button callback.
        This method is run in a separate process with multiprocessing.Process.

        Because the Pi Hat lib sets up a hardware interrupt on the power button
        GPIO pin, it sets up a callback as the ISR. This callback needs to be on
        a separate thread from the DBus main loop otherwise it is taken down with
        a keyboard interrupt signal.
        """

        def _launch_shutdown_menu():
            """ Launch the shutdown menu when the power button is pressed. """

            if not is_enabled.value:
                return

            # FIXME: The problem: The poppa menu eventually pops up on a naked PI
            # with no pihat board connected, right in the middle of Dashboard loading up,
            # grabbing user input and consequently blocking the user completely.
            # Solution: prevent the poppa menu from appearing if the Dashboard
            # has not been running for long enough.

            if time.time() - startup_timestamp < 20:
                return

            # TODO: The env vars bellow are a workaround the fact that Qt5 apps are
            #   stacking on top of each other creating multiple mice, events propagating
            #   below, etc. This hack still leaves a frozen mouse on the screen.
            self.power_button_pressed()
            run_bg(
                'systemd-run'
                ' --setenv=QT_QPA_EGLFS_NO_LIBINPUT=1'
                ' --setenv=QT_QPA_EVDEV_MOUSE_PARAMETERS=grab=1'
                ' /usr/bin/shutdown-menu'
            )

        logger.info('PiHatService: _power_button_thread: Starting..')

        startup_timestamp = time.time()

        kano_hat = KanoHat()
        rc = kano_hat.initialise()
        if rc:
            logger.error(
                'PiHatService: _power_button_thread: Failed to initilise KanoHat'
                ' with rc {}'.format(rc)
            )
        rc = kano_hat.register_power_off_cb(_launch_shutdown_menu)
        if rc:
            logger.error(
                'PiHatService: _power_button_thread: Failed to register power off'
                ' callback with rc {}'.format(rc)
            )

        while True:
            time.sleep(1)
