# use_cases.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#


import os
import sys
import json
import math
import time

from kano.logging import logger
from kano.utils import run_cmd, run_bg

from kano_peripherals.speaker_leds.driver import high_level
from kano_peripherals.speaker_leds.colours import LED_MAGENTA, LED_RED, \
    LED_BLACK, LED_KANO_ORANGE


def notification_start(spec):
    speakerleds_iface = high_level.get_speakerleds_interface()
    if not speakerleds_iface:
        return

    # TODO: a better way of doing this would be to have PRIORITY locks, sorry
    cpu_monitor_running = _is_running('cpu-monitor')
    if cpu_monitor_running:
        _stop('cpu-monitor')

    colours1, colours2 = _get_notification_colours(spec, speakerleds_iface.get_num_leds())

    vf = high_level.pulse(high_level.constant(colours1),
                          high_level.constant(colours2))
    high_level.animate(vf, 60 * 60, 60 * 60 / 2, update_rate=0.005)

    # TODO: a better way of doing this would be to have PRIORITY locks, sorry
    if cpu_monitor_running:
        run_bg('kano-speakerleds cpu-monitor start 5')


def notification_stop():
    _stop('notification')


def initflow_pattern_start(duration, cycles):
    # TODO: a better way of doing this would be to have PRIORITY locks, sorry
    cpu_monitor_running = _is_running('cpu-monitor')
    if cpu_monitor_running:
        _stop('cpu-monitor')

    vf = high_level.rotate(high_level.colourWheel, cycles)
    vf2 = high_level.pulse(vf)
    high_level.animate(vf2, duration, 1.0, update_rate=0.005)

    # TODO: a better way of doing this would be to have PRIORITY locks, sorry
    if cpu_monitor_running:
        run_bg('kano-speakerleds cpu-monitor start 5')


def cpu_monitor_start(update_rate):
    speakerleds_iface = high_level.get_speakerleds_interface()
    if not speakerleds_iface:
        return

    num_leds = speakerleds_iface.get_num_leds()

    vf = high_level.constant([LED_KANO_ORANGE for i in range(num_leds)])
    duration = update_rate
    cycles = duration / 2

    while not high_level.interrupted:
        led_speeds = _get_cpu_led_speeds(0.1, num_leds)

        vf2 = high_level.pulse_each(vf, led_speeds)
        successful = high_level.animate(vf2, duration, cycles)

        if not successful:
            time.sleep(duration)


def cpu_monitor_stop():
    _stop('cpu-monitor')


def off():
    _stop()


def detect():
    speakerleds_iface = high_level.get_speakerleds_interface()
    if not speakerleds_iface:
        return 0

    return 1 if speakerleds_iface.detect() else 0


def _get_notification_colours(spec, num_leds):
    # defaults:
    default_colour1 = LED_RED
    default_colour2 = LED_BLACK

    colours1 = [default_colour1] * num_leds
    colours2 = [default_colour2] * num_leds

    try:
        j = json.loads(spec[0])
        if 'led_colours1' in j:
            colours1 = _validate_colours(j['led_colours1'], num_leds)
        if 'led_colours2' in j:
            colours2 = _validate_colours(j['led_colours2'], num_leds)

        if 'led_colours1' not in j and 'led_colours2' not in j:
            # no colours in spec, so adopt heuristic
            if j['title'] == "Kano World":
                colours1 = [LED_MAGENTA] * num_leds
    except:
        logger.error("failed to decode colour spec {}".format(spec))

    return (colours1, colours2)


def _validate_colours(colours, num_leds):
    """
    Make sure colours is a list of 10 valid colors.
    Allow an exception to be raised if we can't do this.
    """

    if len(colours) == 1:
        colours = [_validate_colour(colours[0])] * num_leds
    elif len(colours) < num_leds:
        raise "not enough colours"
    else:
        colours = map(_validate_colour, colours[:num_leds])
    return colours


def _validate_colour(colour):
    """
    Make sure colour is a tuple of floats.
    Allow an exception to be raised if it isn't.
    """
    return (float(colour[0]), float(colour[1]), float(colour[2]))


def _get_cpu_led_speeds(speed_scale, num_leds):
    # get the top NUM_LEDS processes by CPU usage - PID, %CPU
    cmd = 'ps -eo pid,pcpu --no-headers --sort -pcpu | head -n {}'.format(num_leds)
    output, error, _ = run_cmd(cmd)

    if error:
        logger.error('_get_cpu_led_speeds: cmd error - [{}]'.format(error))
        exit(2)

    try:
        pid_cpu_list = list()

        min_pid = sys.maxint
        max_pid = -sys.maxint - 1

        for line in output.strip().split('\n'):
            parts = line.split()
            pid = int(parts[0])
            cpu = float(parts[1])

            min_pid = min(pid, min_pid)
            max_pid = max(pid, max_pid)

            pid_cpu_list.append([pid, cpu])

        leds = [0 for i in range(num_leds)]
        step = (max_pid + min_pid) / float(num_leds)

        for pid_cpu in pid_cpu_list:
            # calculate the led_index based on the proc PID
            led_index = int(pid_cpu[0] / step)
            # adding the CPU load for multiple PIDs mapped to the same LED
            leds[led_index] += pid_cpu[1] * speed_scale
            # capping the LED speed to 100% CPU load (can be >100%, multicore)
            leds[led_index] = min(math.ceil(leds[led_index]), 100 * speed_scale)

        return leds

    except Exception as e:
        logger.error('_get_cpu_led_speeds: try error - [{}]'.format(e))
        exit(2)


def _stop(option=''):
    cmd = 'pkill --signal INT -f "kano-speakerleds {}"'.format(option)
    os.system(cmd)


def _is_running(option=''):
    cmd = 'pgrep -f "kano-speakerleds {}"'.format(option)
    output, _, _ = run_cmd(cmd)
    return output != ''
