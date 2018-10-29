/**
 *
 * touch_detect.cpp
 *
 * Copyright (C) 2018 Kano Computing Ltd.
 * License: MIT

 * Derived from the xinput tool, which is:
 * Copyright (C) 2007 Peter Hutterer
 * Copyright (C) 2009 Red Hat, Inc.
 * Copyright (C) 1996-1997 by Frederic Lepied
 *
 * Tool to detect a touchscreen is present, and list xinput devices
 *
 * Exit code is 0 when this is the case, 1 when no touch device is present
 * Stdout is xinput ids of the touch devices, one per line.
 *
 */


#include <X11/Xlib.h>
#include <X11/extensions/XInput.h>
#include <X11/extensions/XInput2.h>
#include <stdio.h>
#include <syslog.h>


#include <Kano/TouchDetect/touch_detect.h>


bool Kano::TouchDetect::isTouchSupported() {
    bool found = false;
    Display *display = XOpenDisplay(nullptr);
    int ndevices = 0;

    if (!display) {
        syslog(LOG_ERR | LOG_USER, "touch-detect: could not connect to display\n");
        return false;
    }

    XIDeviceInfo *info = XIQueryDevice(display, XIAllDevices, &ndevices);

    for (int i = 0; i < ndevices; i++) {
        XIDeviceInfo *dev = &info[i];

        if (dev->use != XISlavePointer)
            continue;

        dev->classes, dev->num_classes;

        for (int j = 0; j < dev->num_classes; j++) {
            if (dev->classes[j]->type == XITouchClass) {
                printf("%d\n", dev->deviceid);
                found = true;
            }
        }
    }

    XIFreeDeviceInfo(info);

    if (display)
        XCloseDisplay(display);

    return found;
}
