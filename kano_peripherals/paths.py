# paths.py
#
# Copyright (C) 2015 - 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Includes all the necessary paths for kano-peripherals


from os.path import join


# DBus daemon for kano boards
BUS_NAME = 'me.kano.boards'
OBJECT_BASE_PATH = '/me/kano/boards'

# The Service Manager
SERVICE_MANAGER_OBJECT_NAME = 'ServiceManager'
SERVICE_MANAGER_OBJECT_PATH = join(OBJECT_BASE_PATH, SERVICE_MANAGER_OBJECT_NAME)
SERVICE_MANAGER_IFACE = '.'.join([BUS_NAME, SERVICE_MANAGER_OBJECT_NAME])

# Kano LED Speaker
SPEAKER_LEDS_OBJECT_NAME = 'SpeakerLED'
SPEAKER_LEDS_OBJECT_PATH = join(OBJECT_BASE_PATH, SPEAKER_LEDS_OBJECT_NAME)
SPEAKER_LEDS_IFACE = '.'.join([BUS_NAME, SPEAKER_LEDS_OBJECT_NAME])

# Kano Pi Hat
PI_HAT_OBJECT_NAME = 'PiHat'
PI_HAT_OBJECT_PATH = join(OBJECT_BASE_PATH, PI_HAT_OBJECT_NAME)
PI_HAT_IFACE = '.'.join([BUS_NAME, PI_HAT_OBJECT_NAME])

# CK2 Pro Hat
CK2_PRO_HAT_OBJECT_NAME = 'CK2ProHat'
CK2_PRO_HAT_OBJECT_PATH = join(OBJECT_BASE_PATH, CK2_PRO_HAT_OBJECT_NAME)
CK2_PRO_HAT_IFACE = '.'.join([BUS_NAME, CK2_PRO_HAT_OBJECT_NAME])
