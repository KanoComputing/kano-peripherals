#
# pi_hat.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Module to interface with the ifaces module of the libkano_hat library
#


import os
import ctypes

HAT_LIB = 'libkano_hat.so'

try:
    LIB = ctypes.CDLL(HAT_LIB)
except OSError:
    local_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', '..', HAT_LIB)
    )
    LIB = ctypes.CDLL(local_dir)


class KanoHat(object):
    def __init__(self):
        super(KanoHat, self).__init__()

    @staticmethod
    def initialise():
        LIB.initialise()

    @staticmethod
    def clean_up():
        LIB.clean_up()

    @staticmethod
    def is_connected():
        return LIB.is_hat_connected() == 1

    @staticmethod
    def register_power_off_cb(power_off_fn):
        c_power_off_fn = ctypes.CFUNCTYPE(restype=None)(power_off_fn)
        LIB.register_power_off_cb(c_power_off_fn)

    @staticmethod
    def register_hat_attached_cb(hat_attached_fn):
        c_hat_attached_fn = ctypes.CFUNCTYPE(ctypes.c_int)(hat_attached_fn)
        LIB.register_hat_attached_cb(c_hat_attached_fn)

    @staticmethod
    def register_hat_removed_cb(hat_removed_fn):
        c_hat_removed_fn = ctypes.CFUNCTYPE(ctypes.c_int)(hat_removed_fn)
        LIB.register_hat_detached_cb(c_hat_removed_fn)
