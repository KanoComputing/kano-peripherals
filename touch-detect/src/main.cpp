/**
 * main.cpp
 *
 * Copyright (C) 2018 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
 *
 * Tool to detect a touchscreen is present, and list xinput devices
 *
 * Exit code is 0 when this is the case, 1 when no touch device is present
 * Stdout is xinput ids of the touch devices, one per line.
 *
 */


#include <Kano/TouchDetect/touch_detect.h>


int main(int argc, char *argv[])
{
    if (Kano::TouchDetect::isTouchSupported()) {
        return 0;
    } else {
        return 1;
    }
}
