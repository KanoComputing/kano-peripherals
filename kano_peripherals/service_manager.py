# service_manager.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# A DBus service manager responsible for bringing up and taking down other services.
#
# At startup it will instantiate all given DBus services and once the stop() method
# is called it will ask all running services to clean up and finally quit the
# daemon main loop.


import dbus
import traceback
import dbus.service

from gi.repository import GObject

from kano.logging import logger

from kano_peripherals.paths import SERVICE_MANAGER_OBJECT_PATH, SERVICE_MANAGER_IFACE


class ServiceManager(dbus.service.Object):
    """
    This is a DBus Service provided by kano-boards-daemon.

    It exports an object to /me/kano/boards/ServiceManager and
    its interface to me.kano.boards.ServiceManager

    Does not require sudo.
    """

    def __init__(self, bus_name, mainloop, services):
        """
        Constructor for the ServiceManager.

        Args:
            bus_name - A dbus.service.BusName object to configure the base address.
            mainloop - A Glib.MainLoop object to control the daemon life cycle.
            services - A list of dbus.service.Object to instantiate and run.
        """
        super(ServiceManager, self).__init__(bus_name, SERVICE_MANAGER_OBJECT_PATH)

        self.mainloop = mainloop
        self.services = services

        self.running_services = list()

        # Bring up all services given. TODO: Split up detection routines from their APIs.
        for Service in self.services:
            try:
                service_instance = Service(bus_name)
                self.running_services.append(service_instance)

            except dbus.exceptions.NameExistsException as e:
                logger.warn(
                    'Could not reserve the SystemBus name, most likely another instance'
                    ' of kano-boards-daemon already exists.\n{}'.format(e)
                )
            except Exception as e:
                logger.error(
                    'Unexpected error when starting the services.\n{}'
                    .format(traceback.format_exc())
                )

    # --- Service Management Methods ----------------------------------------------------

    @dbus.service.method(SERVICE_MANAGER_IFACE, out_signature='')
    def stop(self):
        """
        Stop all active services and terminate the daemon.

        After this method returns, some processes will still be running,
        but are guaranteed to terminate shortly (~1sec).
        """
        for service in self.running_services:
            service.stop()

        # Exit the mainloop slightly later, allow the method to return
        # and reply to the caller.
        GObject.idle_add(self.mainloop.quit)

    # --- DBus Interface Testing --------------------------------------------------------

    @dbus.service.method(SERVICE_MANAGER_IFACE, in_signature='', out_signature='b')
    def hello_world(self):
        """
        Use this method to check if the interface to the service
        can reach this object.
        """
        return True
