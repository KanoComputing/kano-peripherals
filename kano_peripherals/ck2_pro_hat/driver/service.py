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
from multiprocessing import Process

from kano.utils import run_bg

from kano_peripherals.lockable_service import LockableService
from kano_peripherals.paths import CK2_PRO_HAT_OBJECT_PATH, CK2_PRO_HAT_IFACE
from kano_pi_hat.ck2_pro_hat import CK2ProHat


class CK2ProHatService(dbus.service.Object):
    """
    This is a DBus Service provided by kano-boards-daemon.

    It exports an object to /me/kano/boards/CK2ProHat and
    its interface to me.kano.boards.CK2ProHat

    Requires sudo.
    """


    def __init__(self, bus_name):
        super(CK2ProHatService, self).__init__(bus_name, CK2_PRO_HAT_OBJECT_PATH)

        self._pi_hat = CK2ProHat()
        self.setup()

        p = Process(target=self._interrupt_thread)
        p.start()

    # --- Board Detection ---------------------------------------------------------------

    @dbus.service.method(CK2_PRO_HAT_IFACE, out_signature='')
    def setup(self):
        """
        Initialise the PiHat board libraries.

        This is called on startup and does not require to be called manually.
        """
        self._pi_hat.initialise()

    @dbus.service.method(CK2_PRO_HAT_IFACE, in_signature='', out_signature='b')
    def detect(self):
        """
        Detect whether the PiHat board is connected.

        Returns:
            connected - bool whether the board is plugged in or not.
        """
        return self._pi_hat.is_connected()

    @dbus.service.method(CK2_PRO_HAT_IFACE, in_signature='', out_signature='b')
    def is_plugged(self):
        """ Same as detect. """
        return self._pi_hat.is_connected()

    # --- DBus Interface Testing --------------------------------------------------------

    @dbus.service.method(CK2_PRO_HAT_IFACE, in_signature='', out_signature='b')
    def hello_world(self):
        """
        Use this method to check if the interface to the service
        can reach this object.

        Required for accurate detection of interface creation.

        FIXME: Should be renamed to better reflect its purpose as an essential
               function rather than what appears to be a test function.
        """
        return True

    # --- Battery Level -----------------------------------------------------------------

    @dbus.service.method(CK2_PRO_HAT_IFACE, in_signature='', out_signature='b')
    def is_battery_low(self):
        """
        Checks the current battery level

        Returns:
            True - the battery level is low
            False - the battery level is high
        """
        return self._pi_hat.is_battery_low()

    @dbus.service.method(CK2_PRO_HAT_IFACE, in_signature='', out_signature='i')
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

    @dbus.service.signal(CK2_PRO_HAT_IFACE, signature='i')
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

    @dbus.service.signal(CK2_PRO_HAT_IFACE, signature='')
    def power_button_pressed(self):
        pass

    # --- Callbacks Thread --------------------------------------------------------------

    def _interrupt_thread(self):
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

        kano_hat = CK2ProHat()
        kano_hat.initialise()

        def battery_changed_cb():
            self.power_level_changed(self.get_battery_level())


        kano_hat.register_power_off_cb(_launch_shutdown_menu)
        # kano_hat.register_low_battery_cb(battery_low_cb)
        # kano_hat.register_battery_charged_cb(battery_charged_cb)
        kano_hat.register_battery_level_changed_cb(battery_changed_cb)

        while True:
            time.sleep(1)
