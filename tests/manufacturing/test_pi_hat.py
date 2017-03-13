# manufacturing_tests.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# A quick manufacturing test for the Pi Hat to ensure LEDs
# are all lighting up in red, green, blue.


import os
import time
import unittest

from kano_peripherals.pi_hat.driver.high_level import get_pihat_interface
from kano_peripherals.wrappers.led_ring.base_animation import BaseAnimation
from kano_peripherals.wrappers.led_ring.init_flow import InitFlow


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
        animation = InitFlow()
        animation.connect()

        response = ''

        while response not in ('yes', 'no', 'y', 'n'):
            animation.start(2.5, 5.0)
            text = 'Did you see the LEDs light up? Please type "y" or "n". Type "r" to replay. '
            response = raw_input(text).lower().strip()

        saw_animation = (response == 'yes' or response == 'y')

        self.assertTrue(saw_animation, 'Animation could not be observed on Pi Hat!')

    @unittest.skipIf(not get_pihat_interface().detect(), 'Board not detected, skipping')
    def test_power_button_press_detected(self):
        self.assertTrue(False, 'Implement this test!')

    # --- Helpers -----------------------------------------------------------------------

    def _attempt_to_recover_daemon(self):
        os.system('/usr/bin/kano-boards-daemon &')
        time.sleep(2)


if __name__ == '__main__':
    unittest.main()
