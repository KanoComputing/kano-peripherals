#
# kano_hat_leds.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Adds LED support for the CK2 Lite Hat
#


import neopixel  # Pip install rpi_ws281x

from kano_pi_hat.kano_hat import KanoHat


class KanoHatLeds(KanoHat):
    LED_COUNT = 10
    LED_PIN = 18

    def __init__(self, brightness=180):
        super(KanoHatLeds, self).__init__()

        self._leds = neopixel.Adafruit_NeoPixel(
            KanoHatLeds.LED_COUNT,
            KanoHatLeds.LED_PIN
        )

        self.set_brightness(brightness)
        self._leds.begin()

    def set_led(self, num, rgb, show=True):
        if len(rgb) != 3:
            # TODO: Should we do something else?
            return False

        red, green, blue = (int(channel * self.brightness) for channel in rgb)
        self._leds.setPixelColorRGB(num, red, green, blue)

        if show:
            self.draw()

        return True

    def set_all_leds(self, values, show=True):
        for idx, val in enumerate(values[:KanoHatLeds.LED_COUNT]):
            self.set_led(idx, val, show=False)

        if show:
            self.draw()

        return True

    def draw(self):
        self._leds.show()

    def set_brightness(self, brightness):
        self.brightness = brightness
        self._leds.setBrightness(brightness)
