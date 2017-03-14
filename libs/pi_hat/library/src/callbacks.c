/**
 *
 * callbacks.c
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Mechanism to wrap multiple callbacks into one call
 *
 */


#include <stdlib.h>

#include "callbacks.h"
#include "err.h"


int new_cb(struct callback ** const cb)
{
    *cb = (callback_list *)malloc(sizeof(callback_list));

    if (*cb == NULL)
        return E_MEMORY_ALLOCATION_ERR;

    (*cb)->cb = NULL;
    (*cb)->next_cb = NULL;

    return SUCCESS;
}


int new_cb_list(callback_list ** const cb_list)
{
    return new_cb((struct callback **)cb_list);
}


int free_cb_list(callback_list ** const cb_list)
{
    if (cb_list == NULL)
        return E_NO_LIST_PROVIDED;

    if (*cb_list == NULL)
        return SUCCESS;

    struct callback *next_cb = (*cb_list)->next_cb;
    free_cb_list(&next_cb);

    free(*cb_list);
    *cb_list = NULL;

    return SUCCESS;
}


int add_cb(callback_list *cb_list, void (*const cb)())
{
    struct callback *current_cb = cb_list;

    if (current_cb == NULL)
        return E_FAIL;

    while (current_cb->next_cb != NULL) {
        current_cb = current_cb->next_cb;
    }

    new_cb(&cb_list->next_cb);
    cb_list->next_cb->cb = cb;
}


/**
 * Takes a callback object and slices every subsequent callback up until next
 */
int slice_cb(struct callback *const prior, struct callback *const next)
{
    struct callback *current_cb = prior->next_cb;

    while (current_cb != NULL && current_cb->next_cb != NULL && current_cb->next_cb != next) {
        current_cb = current_cb->next_cb;
    }

    current_cb->next_cb = NULL;
    free_cb_list(&prior->next_cb);

    prior->next_cb = next;
}


int rm_cb(callback_list **const cb_list, void (*const cb)())
{
    struct callback *current_cb = *cb_list;

    if (current_cb == NULL)
        return E_FAIL;

    if (current_cb->cb == cb) {
        *cb_list = (*cb_list)->next_cb;
        current_cb->next_cb = NULL;
        return free_cb_list(&current_cb);
    }

    struct callback *next_cb;

    while (current_cb->next_cb != NULL) {
        next_cb = current_cb->next_cb;
        if (next_cb->cb == cb) {
            return slice_cb(current_cb, next_cb->next_cb);
        }

        current_cb = current_cb->next_cb;
    }

    return E_CB_NOT_FOUND;
}


int dispatch_cbs(const callback_list * const cb_list)
{
    if (cb_list == NULL)
        return;

    if (cb_list->cb != NULL)
        cb_list->cb();

    dispatch_cbs(cb_list->next_cb);
}
