# service_manager.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# A DBus service manager responsible for bringing up and taking down other services.
#
# The current design specifies that at startup the service will instantiate the
# ServiceManager to look for peripherals. Once a device was found, device
# discovery is stopped and the corresponding service for the device is started.
#
# These are mutually exclusive simply because we do not currently have peripherals
# that can be connected at the same time as others. This should change when we do.
#
# Once the quit() method is called the service will ask all running services to clean
# up and finally quit the daemon main loop, shutting down completely.


import os
import dbus
import traceback
import dbus.service

from kano.logging import logger

from kano_peripherals.base_dbus_service import BaseDBusService
from kano_peripherals.speaker_leds.driver.service import SpeakerLEDsService
from kano_peripherals.pi_hat.driver.service import PiHatService
from kano_pi_hat.kano_hat_leds import KanoHatLeds
from kano_peripherals.ck2_pro_hat.driver.service import CK2ProHatService
from kano_peripherals.device_discovery_service import DeviceDiscoveryService
from kano_peripherals.paths import SERVICE_MANAGER_OBJECT_PATH, SERVICE_API_IFACE, \
    DEVICE_DISCOVERY_OBJECT_PATH, SPEAKER_LEDS_OBJECT_PATH, PI_HAT_OBJECT_PATH, \
    CK2_PRO_HAT_OBJECT_PATH, BUS_NAME


class ServiceManager(BaseDBusService):
    """
    This is a DBus Service provided by kano-boards-daemon.

    It exports an object to /me/kano/boards/ServiceManager and
    its interface to me.kano.boards.ServiceManager

    Does not require sudo.
    """

    def __init__(self, bus_name, mainloop):
        """
        Constructor for the ServiceManager.

        Args:
            bus_name - A dbus.service.BusName object to configure the base address.
            mainloop - A Glib.MainLoop object to control the daemon life cycle.
        """
        super(ServiceManager, self).__init__(bus_name, SERVICE_MANAGER_OBJECT_PATH)

        self.bus_name = bus_name
        self.mainloop = mainloop

        # The KanoHatLeds object cannot be created when the audio module is loaded
        # otherwise the neopixel lib gets mad. The audio module is blacklisted so we
        # load it after the object creation.
        self.pi_hat_lib = KanoHatLeds()
        os.system('modprobe -i snd_bcm2835')

        # All services that need to be started and stopped by this daemon.
        # Add more here as needed.
        self.services = {
            DEVICE_DISCOVERY_OBJECT_PATH: DeviceDiscoveryService,
            SPEAKER_LEDS_OBJECT_PATH: SpeakerLEDsService,
            PI_HAT_OBJECT_PATH: PiHatService,
            CK2_PRO_HAT_OBJECT_PATH: CK2ProHatService
        }
        self.running_services = dict()

        # Start the DeviceDiscoveryService to look for devices.
        if not self._start_service(DEVICE_DISCOVERY_OBJECT_PATH):
            return

        self.connection.add_signal_receiver(
            self._on_device_discovered, 'device_discovered',
            SERVICE_API_IFACE, BUS_NAME, DEVICE_DISCOVERY_OBJECT_PATH
        )

    def _on_device_discovered(self, service_object_path):
        """
        Signal handler for DeviceDiscoveryService's device_discovered signal.

        Stops the DeviceDiscoveryService and brings up the service for the device
        just found. Mutually exclusive only because we don't have devices that can
        be plugged simultaneously currently - change as needed.
        """

        # Stop the DeviceDiscoveryService.
        if not self._stop_service(DEVICE_DISCOVERY_OBJECT_PATH):
            return

        self.connection.remove_signal_receiver(
            self._on_device_discovered, 'device_discovered',
            SERVICE_API_IFACE, BUS_NAME, DEVICE_DISCOVERY_OBJECT_PATH
        )

        # Start the service for the board that was just detected.
        if not self._start_service(service_object_path):
            return

        self.connection.add_signal_receiver(
            self._on_device_disconnected, 'device_disconnected',
            SERVICE_API_IFACE, BUS_NAME, service_object_path
        )

    def _on_device_disconnected(self, service_object_path):
        """
        Signal handler for the device currently plugged device_disconnected signal.

        Stops the service for the device and starts the DeviceDiscoveryService.
        """

        # Stop the service for the device that was just disconnected.
        if not self._stop_service(service_object_path):
            return

        self.connection.remove_signal_receiver(
            self._on_device_disconnected, 'device_disconnected',
            SERVICE_API_IFACE, BUS_NAME, service_object_path
        )

        # Start the DeviceDiscoveryService to look for devices again.
        if not self._start_service(DEVICE_DISCOVERY_OBJECT_PATH):
            return

        self.connection.add_signal_receiver(
            self._on_device_discovered, 'device_discovered',
            SERVICE_API_IFACE, BUS_NAME, DEVICE_DISCOVERY_OBJECT_PATH
        )

    # --- Service Management Methods ----------------------------------------------------

    @dbus.service.method(SERVICE_API_IFACE, out_signature='')
    def quit(self):
        """
        Stop all active services and terminate the daemon.

        After this method returns, some processes will still be running,
        but are guaranteed to terminate shortly (~1sec).
        """
        for service_instance in self.running_services.itervalues():
            service_instance.stop()

        # Lazy import to avoid issue of importing from this module externally.
        from gi.repository import GObject

        # Exit the mainloop slightly later, allow the method to return
        # and reply to the caller.
        GObject.idle_add(self.mainloop.quit)
        self.stop()

    # --- Private Helpers ---------------------------------------------------------------

    def _start_service(self, service_object_path):
        """
        Helper to start a D-Bus service based on its object_path.
        The implementation is specific to this class service base classes.

        Returns:
            successful - bool whether or not the operation succeeded
        """
        if service_object_path not in self.services:
            logger.error(
                'ServiceManager: _start_service: No entry for {} in'
                ' self.services!'.format(service_object_path)
            )
            return False

        try:
            Service = self.services[service_object_path]
            # Pass the KanoHatLeds object to the PiHatService since reinstantiating the
            # object clashes with the audio module.
            if service_object_path == PI_HAT_OBJECT_PATH:
                service_instance = Service(self.bus_name, self.pi_hat_lib)
            else:
                service_instance = Service(self.bus_name)
            self.running_services[service_object_path] = service_instance

        except dbus.exceptions.NameExistsException as e:
            logger.warn(
                'Could not reserve the SystemBus name, most likely another instance'
                ' of kano-boards-daemon already exists.\n{}'.format(e)
            )
            return False
        except Exception as e:
            logger.error(
                'Unexpected error when starting the services.\n{}'
                .format(traceback.format_exc())
            )
            return False

        return True

    def _stop_service(self, service_object_path):
        """
        Helper to stop a D-Bus service based on its object_path.
        The implementation is specific to this class service base classes.

        Returns:
            successful - bool whether or not the operation succeeded
        """
        if service_object_path not in self.running_services:
            logger.error(
                'ServiceManager: _stop_service: No entry for {} in'
                ' self.running_services!'.format(service_object_path)
            )
            return False

        service_instance = self.running_services[service_object_path]

        if not service_instance:
            logger.error(
                'ServiceManager: _stop_service: service_instance is None'
                ' for service_object_path {}'.format(service_object_path)
            )
            return False

        service_instance.stop()
        del self.running_services[service_object_path]

        return True
