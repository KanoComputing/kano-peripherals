# device_discovery_service.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# A DBus service responsible for detecting devices being plugged in.
#
# To check for peripherals, it makes use of the 'quick_detect' static methods
# provided by the device services.


import dbus

from gi.repository import GObject

from kano.logging import logger

from kano_peripherals.base_dbus_service import BaseDBusService
from kano_peripherals.speaker_leds.driver.service import SpeakerLEDsService
from kano_peripherals.pi_hat.driver.service import PiHatService
from kano_peripherals.ck2_pro_hat.driver.service import CK2ProHatService
from kano_peripherals.paths import DEVICE_DISCOVERY_OBJECT_PATH, SERVICE_API_IFACE, \
    PI_HAT_OBJECT_PATH, CK2_PRO_HAT_OBJECT_PATH, SPEAKER_LEDS_OBJECT_PATH


class DeviceDiscoveryService(BaseDBusService):
    """
    This is a DBus Service provided by kano-boards-daemon.

    It exports an object to /me/kano/boards/DeviceDiscovery and
    its interface to me.kano.boards.DeviceDiscovery

    Does not require sudo.
    """

    DISCOVERY_ROUTINE_RATE = 5 * 1000  # milliseconds

    def __init__(self, bus_name):
        """
        Constructor for the DeviceDiscoveryService.

        Args:
            bus_name - A dbus.service.BusName object to configure the base address.
        """
        super(DeviceDiscoveryService, self).__init__(bus_name, DEVICE_DISCOVERY_OBJECT_PATH)

        self.detection_routines = {
            PI_HAT_OBJECT_PATH: PiHatService.quick_detect,
            CK2_PRO_HAT_OBJECT_PATH: CK2ProHatService.quick_detect,
            SPEAKER_LEDS_OBJECT_PATH: SpeakerLEDsService.quick_detect
        }

        GObject.threads_init()
        self.discovery_thread_id = GObject.idle_add(self._discovery_thread)

    def clean_up(self):
        """
        Stop all running (sub)processes and clean up before process termination.
        """
        GObject.source_remove(self.discovery_thread_id)

    def _discovery_thread(self):
        """
        Device discovery routine to look for devices being plugged in.

        When a device is discovered, the 'device_discovered' DBus signal is emitted and
        the routine ends. This method is run in a separate thread with GObject.
        """

        for service_object_path, detection_routine in self.detection_routines.iteritems():
            if detection_routine():
                self.device_discovered(service_object_path)
                return False

        # Did not detect anything, keep calling this method.
        self.discovery_thread_id = GObject.timeout_add(
            self.DISCOVERY_ROUTINE_RATE, self._discovery_thread
        )
        return False

    # --- Signals -----------------------------------------------------------------------

    @dbus.service.signal(SERVICE_API_IFACE, signature='s')
    def device_discovered(self, service_object_path):
        """
        DBus signal to be emitted when a device was discovered.
        """
        logger.info(
            'DeviceDiscoveryService: device_discovered: {}'.format(service_object_path)
        )
