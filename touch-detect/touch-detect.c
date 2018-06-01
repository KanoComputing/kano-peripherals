/**
 *
 * touch-detect
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

int isTouch(void) {
    int found = 1;
    Display     *display = XOpenDisplay(NULL);
    int ndevices=0, i, j;
    if(!display)
    {
        syslog(LOG_ERR | LOG_USER, "touch-detect: could not connect to display\n");
        exit(1);
    }

    XIDeviceInfo *info, *dev;
    info = XIQueryDevice(display, XIAllDevices, &ndevices);
    for(i = 0; i < ndevices; i++)
    {
        dev = &info[i];
        if(dev->use != XISlavePointer)
            continue;
        dev->classes, dev->num_classes;
        for (j = 0; j < dev->num_classes; j++)
        {                
            if(dev->classes[j]->type == XITouchClass)
            {
                printf("%d\n", dev->deviceid);
                found = 0;
            }
        }
    }
    XIFreeDeviceInfo(info);
    if (display)
        XCloseDisplay(display);
    return found;
}

int main(int argc, char * argv[])
{
    return isTouch();
}
