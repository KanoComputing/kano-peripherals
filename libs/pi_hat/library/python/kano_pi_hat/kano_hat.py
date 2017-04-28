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

    @staticmethod
    def initialise():
        LIB.initialise_ck2_lite()

    @staticmethod
    def clean_up():
        LIB.clean_up_ck2_lite()

    @staticmethod
    def is_connected():
        return LIB.is_ck2_lite_connected() == 1

    @staticmethod
    def register_power_off_cb(power_off_fn):
        c_power_off_fn = ctypes.CFUNCTYPE(restype=None)(power_off_fn)
        LIB.register_power_off_cb(c_power_off_fn)
