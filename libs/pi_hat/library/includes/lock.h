/**
 *
 * lock.h
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Lockable resource when using the hat
 *
 */


#ifndef __LOCK_H__
#define __LOCK_H__

static const char *lock_file = "/var/run/lock/kano_hat.lock";

int get_lock();
int release_lock();


#endif  // __LOCK_H__
