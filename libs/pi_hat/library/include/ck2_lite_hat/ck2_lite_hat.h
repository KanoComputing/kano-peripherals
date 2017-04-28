/**
 *
 * kano_hat.h
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * CK2 Lite hat interaction library
 *
 */


#ifndef __KANO_HAT_H__
#define __KANO_HAT_H__


#include <stdbool.h>

#include "power_button.h"


int initialise_ck2_lite(void);
void clean_up_ck2_lite(void);
bool is_ck2_lite_connected(void);


#endif  // __KANO_HAT_H__
