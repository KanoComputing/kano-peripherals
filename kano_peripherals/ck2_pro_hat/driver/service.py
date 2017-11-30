# service.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Low level programming of the Power Hat board through a DBus Service.
#
# It is also responsible for monitoring the battery level, providing OS
# notifications and OS shutdown on low battery. It also launches the
# shutdown-menu dialog when the button on the board is pressed.


import time
import dbus
import dbus.service
from multiprocessing import Process, Value, Event

from kano.logging import logger
from kano.utils import run_bg

from kano_peripherals.base_device_service import BaseDeviceService
from kano_peripherals.ck2_pro_hat.driver.battery_notify_thread import BatteryNotifyThread
from kano_peripherals.paths import CK2_PRO_HAT_OBJECT_PATH, SERVICE_API_IFACE
from kano_pi_hat.ck2_pro_hat import CK2ProHat


class CK2ProHatService(BaseDeviceService):
    """
    This is a DBus Service provided by kano-boards-daemon.

    It exports an object to /me/kano/boards/CK2ProHat and
    its interface to me.kano.boards.CK2ProHat

    Requires sudo.
    """

    # The poll rate for checking if the board is still plugged in.
    DETECT_THREAD_POLL_RATE = 5 * 1000  # milliseconds

    def __init__(self, bus_name):
        """
        Constructor for the CK2ProHatService.

        Given that services should be ready to use when they come online, it also
        performs initialisation and starts subprocesses. It also emits the
        'device_connected' DBus signal as the service is expected to be brought
        up only when the device was discovered.

        Args:
            bus_name - A dbus.service.BusName object to configure the base address.
        """
        super(CK2ProHatService, self).__init__(bus_name, CK2_PRO_HAT_OBJECT_PATH)

        self.ck2_pro_hat = CK2ProHat()
        self.ck2_pro_hat.initialise()

        self.is_power_button_enabled = Value('b', True)
        self.notif_trigger = Event()

        self.interrupt_thread = Process(
            target=self._interrupt_thread,
            args=(self.is_power_button_enabled, self.notif_trigger)
        )
        self.interrupt_thread.start()

        # Thread that triggers notifications when the battery level drops.
        self.battery_notif_thread = BatteryNotifyThread(
            self.notif_trigger,
            self.is_power_button_enabled,
            self.is_battery_low
        )
        self.battery_notif_thread.start()

        # Lazy import to avoid issue of importing from this module externally.
        from gi.repository import GObject

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

        # Lazy import to avoid issue of importing from this module externally.
        from gi.repository import GObject

        GObject.source_remove(self.detect_thread_id)

        self.interrupt_thread.terminate()
        self.battery_notif_thread.join(1.5)

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

        ck2_pro_hat = CK2ProHat()

        if ck2_pro_hat.initialise():
            return False

        connected = ck2_pro_hat.is_connected()
        ck2_pro_hat.clean_up()

        return connected

    @dbus.service.method(SERVICE_API_IFACE, in_signature='', out_signature='b')
    def detect(self):
        """
        Detect whether the PowerHat board is connected.

        Returns:
            connected - bool whether the board is plugged in or not.
        """
        return self.ck2_pro_hat.is_connected()

    @dbus.service.method(SERVICE_API_IFACE, in_signature='', out_signature='b')
    def is_plugged(self):
        """
        TODO: Same as detect, remove.
        """
        return self.ck2_pro_hat.is_connected()

    def _detect_thread(self):
        """
        Poll the detection for PowerHat to know when it is unplugged.

        When the PowerHat is unplugged, the 'device_disconnected' DBus signal is emitted.
        This method is run in a separate thread with GObject.

        TODO: The library for this board uses WiringPi which can do hardware interrupts.
              We could remove this polling thread by having the hardware notify us.
        """
        detected = self.detect()

        if not detected:
            self.device_disconnected(self.get_object_path())

        return detected

    # --- Battery Level -----------------------------------------------------------------

    @dbus.service.method(SERVICE_API_IFACE, in_signature='', out_signature='b')
    def is_battery_low(self):
        """
        Checks the current battery level

        Returns:
            True - the battery level is low
            False - the battery level is high
        """
        return self.ck2_pro_hat.is_battery_low()

    @dbus.service.method(SERVICE_API_IFACE, in_signature='', out_signature='i')
    def get_battery_level(self):
        """
        Checks the current battery level.

        Returns percentage of battery remaining. Currently there are only two
        levels, low or not low, as such this returns one of two values.

        Returns:
            0 - the battery level is low
            100 - the battery level isn't low
        """
        if self.is_battery_low():
            return 0
        else:
            return 100

    @dbus.service.signal(SERVICE_API_IFACE, signature='i')
    def power_level_changed(self, level):
        """
        Signals that the battery level has changed, currently either from high
        to low or low to high.

        Returns percentage of battery remaining

        Returns:
            0 - the battery level is low
            100 - the battery level isn't low
        """
        pass

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

    # --- Callbacks Thread --------------------------------------------------------------

    def _interrupt_thread(self, is_enabled, notif_trigger):
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
            # with no powerhat board connected, right in the middle of Dashboard loading up,
            # grabbing user input and consequently blocking the user completely.
            # Solution: prevent the poppa menu from appearing if the Dashboard
            # has not been running for long enough.

            if time.time() - startup_timestamp < 20:
                return

            self.power_button_pressed()

            # TODO: The env vars bellow are a workaround the fact that Qt5 apps are
            #   stacking on top of each other creating multiple mice, events propagating
            #   below, etc. This hack still leaves a frozen mouse on the screen.
            run_bg(
                'systemd-run'
                ' --setenv=QT_QPA_EGLFS_NO_LIBINPUT=1'
                ' --setenv=QT_QPA_EVDEV_MOUSE_PARAMETERS=grab=1'
                ' /usr/bin/shutdown-menu'
            )

        def battery_changed_cb():
            '''
            Emits a DBus signal to alert others and signals the notification
            thread to do its thing.
            '''
            self.power_level_changed(self.get_battery_level())
            notif_trigger.set()

        startup_timestamp = time.time()

        ck2_pro_hat = CK2ProHat()

        rc = ck2_pro_hat.initialise()
        if rc:
            logger.error(
                'CK2ProHatService: _interrupt_thread: Failed to initialise lib'
                ' with rc {}'.format(rc)
            )
        rc = ck2_pro_hat.register_power_off_cb(_launch_shutdown_menu)
        if rc:
            logger.error(
                'CK2ProHatService: _interrupt_thread: Failed to register power off'
                ' callback1 with rc {}'.format(rc)
            )
        rc = ck2_pro_hat.register_battery_level_changed_cb(battery_changed_cb)
        if rc:
            logger.error(
                'CK2ProHatService: _interrupt_thread: Failed to register battery level'
                ' change callback1 with rc {}'.format(rc)
            )

        # Fire off an update to ensure that the state is initialised correctly
        battery_changed_cb()

        while True:
            time.sleep(1)
