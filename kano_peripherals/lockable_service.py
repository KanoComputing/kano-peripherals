# lockable_service.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# A priority lock service for objects.


import os
import dbus
import dbus.service

from gi.repository import GObject

from kano.logging import logger
from kano.utils import run_cmd

from kano_peripherals.priority_lock import PriorityLock


class LockableService(object):
    """
    A service to enable objects to lock their APIs from different users.

    It uses a PriorityLock object to give the option of multiple users requesting
    different levels of access.
    """

    LOCKING_THREAD_POLL_RATE = 1000 * 10   # ms

    def __init__(self, max_priority=10):
        super(LockableService, self).__init__()

        self.locks = PriorityLock(max_priority=max_priority)

    def lock(self, priority, sender_id=None):
        """
        Block all other API calls with a lower priority.

        Args:
            priority - number representing the priority level (default is 1 to 10).

        Returns:
            True or False if the operation was successful.
        """
        token = ''

        if self.locks.get(priority) is None and sender_id:
            lock_data = self._get_sender_data(sender_id)

            if self.locks.is_empty():
                GObject.timeout_add(self.LOCKING_THREAD_POLL_RATE, self._locking_thread)

            self.locks.put(priority, lock_data)
            token = sender_id  # TODO: is this ok? (security)

            logger.info('LED Speaker locked with priority [{}] by [{}]'
                        .format(priority, lock_data))

        return token

    def unlock(self, sender_id=None):
        """
        Unlock the API from the calling sender.

        Returns:
            True or False if the operation was successful.
        """
        successful = False

        if sender_id:
            lock_data = self._get_sender_data(sender_id)
            successful = self.locks.remove(lock_data)

            if successful:
                logger.info('LED Speaker unlocked from [{}] with PID [{}]'
                            .format(lock_data['cmd'], lock_data['PID']))

        return successful

    def is_locked(self, priority):
        """
        Check if the given priority level or any above are locked.

        Args:
            priority - number representing the priority level (default is 1 to 10).

        Returns:
            True or False if the API is locked on the given priority level.
        """
        return self.locks.contains_above(priority)

    def get_max_lock_priority(self):
        """
        Get the maximum priority level to lock with.

        Returns:
            MAX_PRIORITY_LEVEL - integer number of priority levels
        """
        return self.locks.get_max_lock_priority()

    def get_lock(self):
        """
        Get the lock object used internally to perform the locking.

        Returns:
            locks - a PriorityLock object
        """
        return self.locks

    def _locking_thread(self):
        """
        Check if the locking processes are still alive.
        This method is run in a separate thread with GObject.

        If any process that locked the API has died, it automatically unlocks
        its priority level. It keeps executing as long as there are locks.
        """

        for priority in xrange(len(self.locks)):
            lock_data = self.locks.get(priority)

            if lock_data is not None:
                try:
                    os.kill(lock_data['PID'], 0)

                except OSError:
                    # the current locking process has died
                    logger.warn('[{}] with PID [{}] and priority [{}] died and forgot'
                                ' to unlock the LED Speaker API. Unlocking.'
                                .format(lock_data['cmd'], lock_data['PID'], priority))
                    self.locks.remove_priority(priority)

                except Exception as e:
                    logger.warn('Something unexpected occurred in _locking_thread'
                                ' - [{}]'.format(e))

        # while there are still locks active, keep calling this function indefinitely
        return not self.locks.is_empty()

    def _get_sender_data(self, sender_id):
        """
        Get sender_id, cmd, and PID from the API caller.
        """
        pid = self._get_sender_pid(sender_id)
        cmd = self._get_sender_cmd(pid)

        lock_data = {
            'sender_id': sender_id,
            'PID': pid,
            'cmd': cmd
        }
        return lock_data

    def _get_sender_pid(self, sender_id):
        """
        Get the PID of the process with the sender_id unique bus name.
        """
        sender_pid = None

        if sender_id:
            dbi = dbus.Interface(
                dbus.SystemBus().get_object('org.freedesktop.DBus', '/'),
                'org.freedesktop.DBus'
            )
            sender_pid = int(dbi.GetConnectionUnixProcessID(sender_id))

        return sender_pid

    def _get_sender_cmd(self, sender_pid):
        """
        Get the process name of a given PID. Used for logging (and blaming).
        """
        cmd = 'ps -p {} -o cmd='.format(sender_pid)
        output, _, _ = run_cmd(cmd)
        return output.strip()
