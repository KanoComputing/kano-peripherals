/**
 *
 * ck2_pro_hat.h
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * CK2 Pro hat interaction library
 *
 */


#ifndef __CK2_PRO_HAT_H__
#define __CK2_PRO_HAT_H__


#include <stdbool.h>

#include "battery.h"
#include "power_button.h"


int initialise_ck2_pro(void);
void clean_up_ck2_pro(void);
bool is_ck2_pro_connected(void);


#endif  // __CK2_PRO_HAT_H__
