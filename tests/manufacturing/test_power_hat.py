# test_power_hat.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# A quick manufacturing test for the Power Hat (CK2 Pro) to check
# detection and power button presses.


import os
import time
import unittest
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

from gi.repository import GLib

import kano.colours as colours
from kano_peripherals.ck2_pro_hat.driver.high_level import get_ck2_pro_hat_interface
from kano_peripherals.paths import CK2_PRO_HAT_OBJECT_PATH, CK2_PRO_HAT_IFACE, \
    BUS_NAME as KANO_BOARDS_BUS_NAME


DBUS_MAIN_LOOP = DBusGMainLoop(set_as_default=True)


class TestPowerHat(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        # Get DBus interface to the board and attempt a recovery if it fails.
        self.iface = get_ck2_pro_hat_interface()
        if not self.iface:
            self._attempt_to_recover_daemon()

        self.iface = get_ck2_pro_hat_interface()
        if not self.iface:
            return  # TODO: Stop here, no point going forward. THIS SHOULD NOT HAPPEN!

        # Enable the power button, we'll be using it later.
        self.iface.set_power_button_enabled(True)

    @classmethod
    def teadDownClass(self):
        # Unlock the board API on DBus.
        self.iface.unlock()

    # --- Tests -------------------------------------------------------------------------

    def test_powerhat_board_detected(self):
        header = '''
--------------------------------------------------------------------------------
|                    -[ CK2 Pro ]- TEST: PowerHat detected                     |
--------------------------------------------------------------------------------


'''
        print colours.decorate_with_preset(header, "code")

        self.assertTrue(
            self.iface.detect(),
            'PowerHat board could not be detected!'
        )

    @unittest.skipIf(not get_ck2_pro_hat_interface().detect(), 'Board not detected, skipping')
    def test_power_button_press_detected(self):
        header = '''
--------------------------------------------------------------------------------
|                       -[ CK2 Pro ]- TEST: Power Button                       |
--------------------------------------------------------------------------------


'''
        print colours.decorate_with_preset(header, "code")

        loop = GLib.MainLoop()
        timeout = 30
        self.power_button_failure = False

        def button_pressed():
            loop.quit()

        def abort():
            loop.quit()

            text = colours.decorate_with_preset(
                'Button press not detected within {} seconds.\n'
                'Do you wish to try again? Type "y" or "n".\n'
                .format(timeout), 'warning'
            )
            response = raw_input(text).lower().strip()

            if response not in ('n', 'no'):
                start_loop()
            else:
                self.power_button_failure = True

        def start_loop():
            GLib.timeout_add_seconds(
                priority=GLib.PRIORITY_DEFAULT,
                interval=timeout,
                function=abort
            )

            print '\nPress the power button\n'
            loop.run()

        dbus.SystemBus().add_signal_receiver(
            button_pressed, 'power_button_pressed',
            CK2_PRO_HAT_IFACE, KANO_BOARDS_BUS_NAME, CK2_PRO_HAT_OBJECT_PATH
        )

        start_loop()

        if self.power_button_failure:
            fail_msg = 'Power button press not detected'
            print colours.decorate_with_preset(fail_msg, 'fail')
            self.fail(fail_msg)

    # --- Helpers -----------------------------------------------------------------------

    def _attempt_to_recover_daemon(self):
        os.system('/usr/bin/kano-boards-daemon &')
        time.sleep(2)


if __name__ == '__main__':
    unittest.main()
