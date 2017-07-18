# paths.py
#
# Copyright (C) 2015 - 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Includes all the necessary paths for kano-peripherals


from os.path import join


# DBus daemon for kano boards
BASE_ADDRESS_PARTS = ['me', 'kano', 'boards']
BUS_NAME = '.'.join(BASE_ADDRESS_PARTS)
OBJECT_BASE_PATH = '/' + '/'.join(BASE_ADDRESS_PARTS)

# Interfaces exposed by the services
API_IFACE_NAME = 'API'
SERVICE_API_IFACE = '.'.join([BUS_NAME, API_IFACE_NAME])

# The Service Manager
SERVICE_MANAGER_OBJECT_NAME = 'ServiceManager'
SERVICE_MANAGER_OBJECT_PATH = join(OBJECT_BASE_PATH, SERVICE_MANAGER_OBJECT_NAME)

# The Device Discovery Service
DEVICE_DISCOVERY_OBJECT_NAME = 'DeviceDiscovery'
DEVICE_DISCOVERY_OBJECT_PATH = join(OBJECT_BASE_PATH, DEVICE_DISCOVERY_OBJECT_NAME)

# Kano LED Speaker
SPEAKER_LEDS_OBJECT_NAME = 'SpeakerLED'
SPEAKER_LEDS_OBJECT_PATH = join(OBJECT_BASE_PATH, SPEAKER_LEDS_OBJECT_NAME)

# Kano Pi Hat
PI_HAT_OBJECT_NAME = 'PiHat'
PI_HAT_OBJECT_PATH = join(OBJECT_BASE_PATH, PI_HAT_OBJECT_NAME)

# CK2 Pro Hat
CK2_PRO_HAT_OBJECT_NAME = 'CK2ProHat'
CK2_PRO_HAT_OBJECT_PATH = join(OBJECT_BASE_PATH, CK2_PRO_HAT_OBJECT_NAME)
