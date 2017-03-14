/**
 *
 * callbacks.h
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Mechanism to wrap multiple callbacks into one call
 *
 */


#ifndef __CALLBACKS_H__
#define __CALLBACKS_H__


typedef struct callback {
    void (*cb)();
    struct callback *next_cb;
} callback_list;


int new_cb(struct callback ** const cb);
int new_cb_list(callback_list ** const cb_list);
int free_cb_list(callback_list ** const cb_list);
int add_cb(callback_list * const cb_list, void (* const cb)());
int slice_cb(struct callback *const prior, struct callback *const next);
int rm_cb(callback_list **const cb_list, void (*const cb)());
int dispatch_cbs(const callback_list * const cb_list);


#endif
