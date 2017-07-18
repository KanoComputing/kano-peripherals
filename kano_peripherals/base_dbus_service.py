# base_dbus_service.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The base class for all D-Bus services used in this project.


import dbus

from kano_peripherals.paths import SERVICE_API_IFACE


class BaseDbusService(dbus.service.Object):
    """
    The base class for all D-Bus services used in this project.
    """

    def __init__(self, bus_name, object_path):
        """
        Constructor for the BaseDbusService.

        Args:
            bus_name    - A dbus.service.BusName object to configure the base address.
            object_path - DBus object path as expected by dbus.service.Object constructor
        """
        super(BaseDbusService, self).__init__(bus_name, object_path)

    @dbus.service.method(SERVICE_API_IFACE, in_signature='', out_signature='b')
    def is_iface_valid(self):
        """
        Check if an interface to this DBus service is able to reach the service.

        Raises:
            dbus.exceptions.UnknownMethodException - if the interface cannot reach this
                service because it is not online
        Returns:
            true - if the interface can reach the service and is usable
        """
        return True

    def stop(self):
        """
        Stop the DBus service and take it offline.

        After calling this method, it is expected that all references to the service
        instance are removed and garbage collected. The service will then become
        unreachable over DBus.
        """
        self.clean_up()
        self.remove_from_connection()

    def clean_up(self):
        """
        A stub for subclasses to perform any clean up when the service is taken down.
        """
        pass

    def get_object_path(self):
        """
        Getter for the DBus service object path.

        Returns:
            object_path - str the object path at which the service is available
        """
        return self.__dbus_object_path__
