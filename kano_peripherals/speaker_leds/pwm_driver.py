# speaker_leds/low_level.py
#
# Copyright (c) 2012-2013 Limor Fried, Kevin Townsend and Mikey Sklar for Adafruit Industries.
# Copyright (C) 2015 Kano Computing Ltd.
# License: 3 Clause BSD
#

# This is derived from https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/blob/master/Adafruit_PWM_Servo_Driver/Adafruit_PWM_Servo_Driver.py

# It is modified:
#  * To strip out an intermediate layer
#  * It is only used for setup instead of actual LED programming
#  * It configures the PWM chip for autoincrement, to allow block transfers.



import math
import time

class PWM:
    # Registers/etc.
    __MODE1              = 0x00
    __MODE2              = 0x01
    __SUBADR1            = 0x02
    __SUBADR2            = 0x03
    __SUBADR3            = 0x04
    __PRESCALE           = 0xFE
    __LED0_ON_L          = 0x06
    __LED0_ON_H          = 0x07
    __LED0_OFF_L         = 0x08
    __LED0_OFF_H         = 0x09
    __ALL_LED_ON_L       = 0xFA
    __ALL_LED_ON_H       = 0xFB
    __ALL_LED_OFF_L      = 0xFC
    __ALL_LED_OFF_H      = 0xFD

    # Bits
    __RESTART            = 0x80
    __AI                 = 0x20
    __SLEEP              = 0x10
    __ALLCALL            = 0x01
    __INVRT              = 0x10
    __OUTDRV             = 0x04

    def softwareReset(self):
        "Sends a software reset (SWRST) command to all the servo drivers on the bus"

        # observed values after reset:
        #  MODE1  = 0x11 (ALLCALL | SLEEP)
        #  MODE2  = 0x4  (OUTDRV)
        #  PRESCALE  = 0x1E
        
        self.i2cbus.write_byte(0, 0x06)        # SWRST

    def  __init__(self, bus, address, debug = False):
        self.address = address
        self.i2cbus = bus
        self.debug = debug

    def reset(self):
        self.setAllPWM(0, 0)
        self.i2cbus.write_byte_data(self.address, self.__MODE2, 0)
        self.i2cbus.write_byte_data(self.address, self.__MODE1, self.__ALLCALL | self.__AI)
        time.sleep(0.005)                                       # wait for oscillator

        mode1 = self.i2cbus.read_byte_data(self.address, self.__MODE1)
        mode1 = mode1 & ~self.__SLEEP                 # wake up (reset sleep)
        self.i2cbus.write_byte_data(self.address, self.__MODE1, mode1)
        time.sleep(0.005)                             # wait for oscillator
      
    def setPWMFreq(self, freq):
        "Sets the PWM frequency"
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        if (self.debug):
            print "Setting PWM frequency to %d Hz" % freq
            print "Estimated pre-scale: %d" % prescaleval
        prescale = math.floor(prescaleval + 0.5)
        if (self.debug):
            print "Final pre-scale: %d" % prescale

        oldmode = self.i2cbus.read_byte_data(self.address, self.__MODE1)
        newmode = (oldmode & 0x7F) | 0x10             # sleep
        self.i2cbus.write_byte_data(self.address, self.__MODE1, newmode)        # go to sleep
        self.i2cbus.write_byte_data(self.address, self.__PRESCALE, int(math.floor(prescale)))
        self.i2cbus.write_byte_data(self.address, self.__MODE1, oldmode)
        time.sleep(0.005)
        self.i2cbus.write_byte_data(self.address, self.__MODE1, oldmode | 0x80)

    def setAllPWM(self, on, off):
        "Sets a all PWM channels"
        self.i2cbus.write_byte_data(self.address, self.__ALL_LED_ON_L, on & 0xFF)
        self.i2cbus.write_byte_data(self.address, self.__ALL_LED_ON_H, on >> 8)
        self.i2cbus.write_byte_data(self.address, self.__ALL_LED_OFF_L, off & 0xFF)
        self.i2cbus.write_byte_data(self.address, self.__ALL_LED_OFF_H, off >> 8)
