# test_pi_hat.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# A quick manufacturing test for the Pi Hat to ensure LEDs
# are all lighting up in red, green, blue.


import os
import time
import unittest
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

from gi.repository import GLib

import kano.colours as colours

from kano_peripherals.pi_hat.driver.high_level import get_pihat_interface
from kano_peripherals.wrappers.led_ring.base_animation import BaseAnimation
from kano_peripherals.wrappers.led_ring.init_flow import InitFlow
from kano_peripherals.paths import PI_HAT_OBJECT_PATH, PI_HAT_IFACE, \
    BUS_NAME as PI_HAT_BUS_NAME


DBUS_MAIN_LOOP = DBusGMainLoop(set_as_default=True)

RED = (0.5, 0.0, 0.0)
GREEN = (0.0, 0.5, 0.0)
BLUE = (0.0, 0.0, 0.5)


class TestPiHat(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        # Stop any possible running animations.
        BaseAnimation.stop('')

        # Get DBus interface to the board and attempt a recovery if it fails.
        self.iface = get_pihat_interface()
        if not self.iface:
            self._attempt_to_recover_daemon()

        self.iface = get_pihat_interface()
        if not self.iface:
            pass  # TODO: Stop here, no point going forward. THIS SHOULD NOT HAPPEN!

        # Lock the board API so nothing can interfere.
        self.iface.lock(self.iface.get_max_lock_priority())

    @classmethod
    def teadDownClass(self):
        # Unlock the board API on DBus.
        self.iface.unlock()

    # --- Tests -------------------------------------------------------------------------

    def test_pihat_board_detected(self):
        self.assertTrue(self.iface.detect(), 'Pi Hat board could not be detected!')

    @unittest.skipIf(not get_pihat_interface().detect(), 'Board not detected, skipping')
    def test_run_rgb_sequence(self):
        header = '''
--------------------------------------------------------------------------------
|                        -[ CK2 Lite ]- TEST: LED Ring                         |
--------------------------------------------------------------------------------


'''
        print colours.decorate_with_preset(header, "code")

        def led_animation():
            time.sleep(1)
            self.iface.set_all_leds([RED] * self.iface.get_num_leds())
            time.sleep(1)
            self.iface.set_all_leds([GREEN] * self.iface.get_num_leds())
            time.sleep(1)
            self.iface.set_all_leds([BLUE] * self.iface.get_num_leds())
            time.sleep(1)
            self.iface.set_leds_off()

        response = ''
        fail_count = 0

        while response not in ('yes', 'y'):
            led_animation()

            text = 'Did you see all the LEDs light up? Please type "y" or "n". Type "r" to replay. '
            text = colours.decorate_with_preset(text, "warning")
            response = raw_input(text).lower().strip()

            if response in ('no', 'n'):
                # Setting LEDs can sometimes fail on the first run, trying again
                fail_count += 1

                if fail_count > 1:
                    break
                else:
                    print colours.decorate_with_preset(
                        "Trying again",
                        "warning"
                    )

        saw_animation = (response == 'yes' or response == 'y')

        self.assertTrue(saw_animation, 'Animation could not be observed on Pi Hat!')

    @unittest.skipIf(not get_pihat_interface().detect(), 'Board not detected, skipping')
    def test_power_button_press_detected(self):
        header = '''
--------------------------------------------------------------------------------
|                      -[ CK2 Lite ]- TEST: Power Button                       |
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
            button_pressed, 'power_button_pressed', PI_HAT_IFACE,
            PI_HAT_BUS_NAME, PI_HAT_OBJECT_PATH
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
