/**
 *
 * lock.c
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Lockable resource when using the hat
 *
 */


#include <sys/file.h>

#include "lock.h"
#include "err.h"


int lock_fd = -1;


int get_lock()
{
    if (lock_fd != -1)
        return E_ALREADY_INITIALISED;

    lock_fd = open(lock_file, O_RDWR | O_CREAT | O_CLOEXEC, S_IRUSR | S_IWUSR);

    if (lock_fd == -1)
        return E_COULD_NOT_GET_LOCK;

    if (flock(lock_fd, LOCK_EX | LOCK_NB) == -1) {
        close(lock_fd);
        lock_fd = -1;
        return E_COULD_NOT_GET_LOCK;
    }

    return SUCCESS;
}


int release_lock()
{
    if (lock_fd == -1)
        return SUCCESS;

    flock(lock_fd, LOCK_UN | LOCK_NB);
    close(lock_fd);
    lock_fd = -1;

    return SUCCESS;
}
