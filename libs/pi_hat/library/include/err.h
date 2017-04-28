/**
 *
 * err.h
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Errors produced by the hat
 *
 */


#ifndef __ERR_H__
#define __ERR_H__


enum {
    SUCCESS,
    E_FAIL,
    E_HAT_NOT_ATTACHED,
    E_NO_LIST_PROVIDED,
    E_MEMORY_ALLOCATION_ERR,
    E_CB_NOT_FOUND,
    E_ALREADY_INITIALISED,
    E_LIBRARY_INITIALISED_ELSEWHERE,
    E_COULD_NOT_GET_LOCK
};


#endif  // __ERR_H__
