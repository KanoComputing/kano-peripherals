#
# ck2_pro_hat.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Module to interface with the CK2 Pro Hat
#


import ctypes

from kano_pi_hat.lib import LIB


class CK2ProHat(object):

    def __init__(self):
        super(CK2ProHat, self).__init__()

        self.callbacks = list()

    def initialise(self):
        return LIB.initialise_ck2_pro()

    def clean_up(self):
        LIB.clean_up_ck2_pro()
        del self.callbacks[:]

    def is_connected(self):
        return LIB.is_ck2_pro_connected() == 1

    def is_battery_low(self):
        return LIB.is_battery_low() == 1

    def register_power_off_cb(self, power_off_fn):
        c_power_off_fn = ctypes.CFUNCTYPE(restype=None)(power_off_fn)
        self.callbacks.append(c_power_off_fn)
        return LIB.register_power_off_cb(c_power_off_fn)

    def register_battery_level_changed_cb(self, battery_change_fn):
        c_battery_change_fn = ctypes.CFUNCTYPE(restype=None)(battery_change_fn)
        self.callbacks.append(c_battery_change_fn)
        return LIB.register_battery_level_changed_cb(c_battery_change_fn)
