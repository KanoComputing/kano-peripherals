# test_ck2_pro_hat.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# A quick manufacturing test for the CK2 Pro Hat to ensure correct functionality
# on the production line


import os
import time
import unittest

from boot_test import *
from kano_peripherals.ck2_pro_hat.driver.high_level import \
    get_ck2_pro_hat_interface

import kano.colours as colours


class TestProHat(BootTest):

    @classmethod
    def setUpClass(cls):
        # Get DBus interface to the board and attempt a recovery if it fails.
        cls.iface = get_ck2_pro_hat_interface()
        if not cls.iface:
            cls._attempt_to_recover_daemon()

        cls.iface = get_ck2_pro_hat_interface()
        if not cls.iface:
            pass  # TODO: Stop here, no point going forward. THIS SHOULD NOT HAPPEN!

    # --- Tests ----------------------------------------------------------------

    def test_pro_hat_board_detected(self):
        self.bootAssertTrue(
            self.iface.detect(),
            'CK2 Pro Hat board could not be detected!'
        )
        self._test_done()

    # --- Helpers --------------------------------------------------------------

    @staticmethod
    def _attempt_to_recover_daemon():
        os.system('/usr/bin/kano-boards-daemon &')
        time.sleep(2)


if __name__ == '__main__':
    unittest.main()
