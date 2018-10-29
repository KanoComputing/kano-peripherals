/**
 * example.cpp
 *
 * Copyright (C) 2018 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
 *
 * Simple program to test Conan packaging setup
 *
 */


#include <iostream>

#include <Kano/TouchDetect/touch_detect.h>


int main(int argc, char *argv[])
{
    std::cout << Kano::TouchDetect::isTouchSupported();
}
