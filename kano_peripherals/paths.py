# paths.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Includes all the necessary paths for kano-peripherals


from os.path import join


# dbus daemon for kano boards
BUS_NAME = 'me.kano.boards'
OBJECT_BASE_PATH = '/me/kano/boards'

# Kano LED Speaker
SPEAKER_LEDS_OBJECT_NAME = 'SpeakerLED'
SPEAKER_LEDS_OBJECT_PATH = join(OBJECT_BASE_PATH, SPEAKER_LEDS_OBJECT_NAME)
SPEAKER_LEDS_IFACE = '.'.join([BUS_NAME, SPEAKER_LEDS_OBJECT_NAME])
