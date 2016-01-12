# priority_lock.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# A priority locking mechanism.


from kano.logging import logger


class PriorityLock(object):
    """
    This is a priority locking mechanism.

    Locks with the highest priority are considered to have priority.
    They need to store a non-None object which can hold arbitrary data.
    """

    def __init__(self, max_priority=10):
        self.max_priority = max_priority

        # initialising instance vars
        self.top_priority = 0
        self.num_locks = 0

        self.locks = [None for i in xrange(max_priority + 1)]

    def __len__(self):
        """ Length of the object is given by the number of priority levels. """
        return len(self.locks)

    def is_empty(self):
        """
        Get locks status.

        Returns:
            True or False if there are any active locks.
        """
        return self.locks[self.top_priority] is None

    def contains(self, data):
        """
        Check if the lock data object is present.

        Args:
            data - a non-None object to hold data about the lock.

        Returns:
            True or False if any lock contains the given data object.
        """
        if data is None:
            return False

        for priority in xrange(0, self.top_priority):
            if data == self.locks[priority]:
                return True

        return False

    def contains_above(self, priority):
        """
        Check lock status on priority level.

        Args:
            priority - integer between 1 and max_priority.

        Returns:
            True or False if there is an active lock on the given priority level or above.

        Throws:
            ValueError - if priority is not a number.
        """
        priority = self._standardise_priority(priority)

        return priority <= self.top_priority

    def get(self, priority=None):
        """
        Get a priority lock.
        If priority is not given, returns the lock with top_priority.

        Args:
            priority - integer between 1 and max_priority.

        Returns:
            Lock data object or None if there is no lock active.

        Throws:
            ValueError - if priority is not a number.
        """
        priority = self.top_priority if priority is None else self._standardise_priority(priority)

        return self.locks[priority]

    def get_all(self):
        """
        Get the internal list of locks.

        Returns:
            locks - list of lock data/None objects for locked/unlocked priority levels.
        """
        return self.locks

    def put(self, priority, data):
        """
        Add a lock with a given priority and data.
        Locks with the highest priority are considered to have priority.

        Args:
            priority - integer between 1 and max_priority.
            data - a non-None object to hold data about the lock.

        Returns:
            True or False if the operation was successful.

        Throws:
            ValueError - if priority is not a number.
        """
        if data is None:
            return False

        priority = self._standardise_priority(priority)
        successful = True

        try:
            if self.locks[priority] is None:
                self.num_locks += 1
                self.locks[priority] = data

                if priority > self.top_priority:
                    self.top_priority = priority
            else:
                successful = False

        except IndexError:
            logger.error('There was an unintentional IndexError in put() with'
                         ' priority [{}] and locks [{}]. Check the code!'
                         .format(priority, self.locks))
            successful = False

        return successful

    def remove(self, data):
        """
        Remove a lock which has the given data.

        Args:
            data - the non-None object stored by the lock to be removed.

        Returns:
            True or False if the operation was successful.
        """
        if data is None:
            return False

        successful = False
        top_priority_removed = False

        try:
            for priority in xrange(self.top_priority, 0, -1):
                if data == self.locks[priority]:
                    self.num_locks -= 1
                    self.locks[priority] = None
                    successful = True

                    if priority == self.top_priority:
                        top_priority_removed = True

                if self.locks[priority] is None and top_priority_removed:
                    self.top_priority -= 1
                else:
                    top_priority_removed = False

        except IndexError:
            logger.error('There was an unintentional IndexError in remove() with'
                         ' priority [{}] and locks [{}]. Check the code!'
                         .format(priority, self.locks))
            successful = False

        return successful

    def remove_priority(self, priority):
        """
        Remove a lock with a given priority.
        This should be slightly faster than calling remove().

        Args:
            priority - priority of the lock to be removed.

        Returns:
            True or False if the operation was successful.
        """
        priority = self._standardise_priority(priority)
        successful = True

        try:
            if self.locks[priority] is not None:
                self.num_locks -= 1
                self.locks[priority] = None

                if priority == self.top_priority:
                    for index in xrange(self.top_priority, -1, -1):
                        self.top_priority = index
                        if self.locks[index] is not None:
                            break
            else:
                successful = False

        except IndexError:
            logger.error('There was an unintentional IndexError in remove_priority() with'
                         ' priority [{}] and locks [{}]. Check the code!'
                         .format(priority, self.locks))
            successful = False

        return successful

    def _standardise_priority(self, priority):
        """ Truncate the priority to fit set interval """

        priority = int(priority)

        priority = priority if (priority < self.max_priority) else self.max_priority
        priority = priority if (priority > 0) else 1

        return priority

    def __repr__(self):
        """ The object string representation. For testing, not production. """

        locks_string = ''
        for index in xrange(len(self.locks)):
            locks_string += '    {}. {},\n'.format(index, self.locks[index])

        return 'PriorityLock: \n' \
               '  self.top_priority is {} \n' \
               '  self.num_locks is {} \n' \
               '  self.locks is [\n{}]'.format(
                   self.top_priority, self.num_locks, locks_string)
