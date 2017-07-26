#
# kano_hat.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Module to interface with the CK2 Lite Hat
#


import ctypes

from kano_pi_hat.lib import LIB


class KanoHat(object):

    def __init__(self):
        super(KanoHat, self).__init__()

        # List of registered callback pointers. These need to be kept otherwise
        # Python will garbage collect them.
        self.callbacks = list()

    def initialise(self):
        return LIB.initialise_ck2_lite()

    def clean_up(self):
        LIB.clean_up_ck2_lite()
        del self.callbacks[:]

    def is_connected(self):
        return LIB.is_ck2_lite_connected() == 1

    def register_power_off_cb(self, power_off_fn):
        c_power_off_fn = ctypes.CFUNCTYPE(restype=None)(power_off_fn)
        self.callbacks.append(c_power_off_fn)
        return LIB.register_power_off_cb(c_power_off_fn)
