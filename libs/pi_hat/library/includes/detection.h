/**
 *
 * detection.h
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Hat detection and connectivity functions
 *
 */


#ifndef __DETECTION_H__
#define __DETECTION_H__


int initialise_detection();
int clean_up_detection();
int is_hat_connected(void);
void detect_hat_state(void);
int register_hat_attached_cb(void cb(void));
int register_hat_detached_cb(void cb(void));


#endif  // __DETECTION_H__
