# battery_notify_thread.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Thread to provide notifications about the system's battery level
#

import os
import threading
from gi.repository import GLib

from kano.notifications import display_generic_notification, \
    close_current_notification, update_current_notification


SHUTDOWN_WARN_TIME = 5 * 60  # seconds
SHUTDOWN_TIMEOUT = 60  # seconds
ERROR_NOTIF_IMAGE = '/usr/share/kano-peripherals/assets/low_battery_alert.png'
ERROR_NOTIF_SOUND = '/usr/share/kano-media/sounds/kano_error.wav'


class BatteryNotifyThread(threading.Thread):
    '''
    A simple thread which queues a notification in the main thread whenever
    the interrupt multiprocessing.Process triggers one.

    Used to alert the user of the battery level (or lack of it)

    Required because the `Process` can't queue things directly.
    '''

    def __init__(self, notif_trigger, shutdown_enabled, is_battery_low):
        '''
        Params:
            notif_trigger (multiprocessing.Event):
                An event to trigger that a new notification may be required. As
                soon as the event is `set`, the thread will consider itself in
                a state of requiring notifications.

            shutdown_enabled (multiprocessing.Value):
                Flag to deterimine if the kit should shutdown. To be used to
                prevent the subsequent shutdown notification (and actual
                poweroff) from being created. Often will match those occasions
                where the power button is disabled.

            is_battery_low (function pointer):
                Function to retrieve the battery level. Should return true if
                the battery is at a dangerous level, false otherwise.
        '''
        super(BatteryNotifyThread, self).__init__()

        self._notif_trigger = notif_trigger
        self._shutdown_enabled = shutdown_enabled
        self._is_battery_low = is_battery_low

        self._notif_open = threading.Event()
        self.daemon = True
        self.shutdown_time_remaining = None


    def run(self):
        '''
        Starts the thread waiting for a notification event to be triggered.
        '''

        while True:
            if not self._notif_trigger.wait(1):
                continue

            GLib.idle_add(
                self.create_notif,
                priority=GLib.PRIORITY_HIGH_IDLE
            )

            self._notif_trigger.clear()


    def create_notif(self):
        '''
        Triggers a notification to be opened or removed based on the battery
        state

        NB: Must be called from the main thread as the notification has a
            timeout which fails if called from a threading.Thread or
            multiprocessing.Process, as such, it should be `idle_add`ed from
            `Thread`s and requires a more complicated procedure from
            `Process`es.
        '''

        if self._is_battery_low():
            if self._notif_open.is_set():
                return

            display_generic_notification(
                'Plug In Your Kit!',
                'Your kit has a low battery and will turn off soon!',
                image=ERROR_NOTIF_IMAGE,
                sound=ERROR_NOTIF_SOUND,
                urgency='critical'
            )

            if self._shutdown_enabled.value:
                GLib.timeout_add_seconds(
                    SHUTDOWN_WARN_TIME,
                    self._low_power_shutdown
                )

            self._notif_open.set()
        else:
            close_current_notification()
            self._notif_open.clear()


    @staticmethod
    def _update_countdown(time_remaining, create=False):
        '''
        Provides an update on the shutdown timer via a notification
        '''

        shutdown_title = 'Kit is shutting down!'
        shutdown_msg = 'Your kit will shutdown in {sec} seconds'

        if create:
            close_current_notification()
            display_generic_notification(
                shutdown_title,
                shutdown_msg.format(sec=time_remaining),
                image=ERROR_NOTIF_IMAGE,
                sound=ERROR_NOTIF_SOUND,
                urgency='critical'
            )
        else:
            update_current_notification(
                desc=shutdown_msg.format(sec=time_remaining)
            )


    def _low_power_shutdown(self):
        '''
        Handles the shutdown countdown when the power is low
        '''

        if not self._is_battery_low():
            # No longer in the danger zone, cancel all timers
            self.shutdown_time_remaining = None
            close_current_notification()
            self._notif_open.clear()

            return False


        if not self.shutdown_time_remaining:
            # Initialise the shutdown timer
            self.shutdown_time_remaining = SHUTDOWN_TIMEOUT
            self._update_countdown(self.shutdown_time_remaining, create=True)
            GLib.timeout_add_seconds(
                1,
                self._low_power_shutdown
            )

            return False  # Cancel the 5 minute timer, keep the 1 second one


        self.shutdown_time_remaining -= 1

        if self.shutdown_time_remaining > 0:
            self._update_countdown(self.shutdown_time_remaining)

            return True


        # The timer has expired, actually shutdown
        update_current_notification(
            title='Shutting down',
            desc='Your kit ran out of power'
        )
        os.system("sudo poweroff")

        return False
