/**
 * touch_detect.cpp
 *
 * Copyright (C) 2018 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
 *
 * Detect if a touch device is present
 *
 */


#include <Kano/TouchDetect/touch_detect.h>

#include <iostream>


bool Kano::TouchDetect::isTouchSupported() {
    std::cout << "Not implemented for OSX, returning true\n";
    return true;
}
