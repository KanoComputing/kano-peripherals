# base_device_service.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The base class for all D-Bus services for devices supported in this project.


import dbus

from kano.logging import logger

from kano_peripherals.base_dbus_service import BaseDbusService
from kano_peripherals.paths import SERVICE_API_IFACE


class BaseDeviceService(BaseDbusService):
    """
    The base class for all D-Bus services for devices supported in this project.
    """

    def __init__(self, bus_name, object_path):
        """
        Constructor for the BaseDeviceService.

        Args:
            bus_name    - A dbus.service.BusName object to configure the base address.
            object_path - DBus object path as expected by dbus.service.Object constructor
        """
        super(BaseDeviceService, self).__init__(bus_name, object_path)

    # --- Device Detection ---------------------------------------------------------------

    @classmethod
    def quick_detect(cls):
        """
        Static method stub for device services to perform detection outside the service.

        This method is indended to be used when the service is offline and an external
        detection routine checks for all devices. This is currently used in the
        DeviceDiscoveryService.

        All subclasses are required to implement this method!
        """
        logger.error(
            '{}: quick_detect: Not implemented, inherited from BaseDeviceService'
            .format(cls.__name__)
        )
        return False

    @dbus.service.method(SERVICE_API_IFACE, in_signature='', out_signature='b')
    def detect(self):
        """
        Stub for device services to detect whether the peripherals are plugged in.

        All subclasses are required to implement this method!
        """
        logger.error(
            '{}: detect: Not implemented, inherited from BaseDeviceService'
            .format(self.__class__.__name__)
        )
        return False

    # --- Signals -----------------------------------------------------------------------

    @dbus.service.signal(SERVICE_API_IFACE, signature='s')
    def device_connected(self, service_object_path):
        """
        DBus signal to be emitted when the device was plugged in.
        """
        logger.info(
            '{}: device_connected: {}'
            .format(self.__class__.__name__, service_object_path)
        )

    @dbus.service.signal(SERVICE_API_IFACE, signature='s')
    def device_disconnected(self, service_object_path):
        """
        DBus signal to be emitted when the device was unplugged.
        """
        logger.info(
            '{}: device_disconnected: {}'
            .format(self.__class__.__name__, service_object_path)
        )
