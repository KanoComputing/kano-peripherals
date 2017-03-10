# cpu_monitor.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# TODO: Description


import sys
import math
import time

from kano_settings.config_file import get_setting
from kano.utils import run_cmd
from kano.logging import logger

from kano_peripherals.wrappers.led_ring.base_animation import BaseAnimation
from kano_peripherals.return_codes import *

# TODO: Move these
from kano_peripherals.speaker_leds.colours import LED_MAGENTA, LED_RED, \
    LED_BLACK, LED_KANO_ORANGE


class CpuMonitor(BaseAnimation):
    """
    """

    LOCK_PRIORITY = 1

    def __init__(self):
        super(CpuMonitor, self).__init__()

    def start(self, update_rate, check_settings, retry_count):
        """
        """
        if not self.iface and not self.connect():
            logger.error('LED Ring: CpuMonitor: Could not aquire dbus interface!')
            return RC_FAILED_ANIM_GET_DBUS

        if check_settings:
            cpu_monitor_on = self._get_cpu_monitor_setting()
            if not cpu_monitor_on:
                return

        locked = self.iface.lock(self.LOCK_PRIORITY)
        if not locked:
            logger.error('LED Ring: CpuMonitor: Could not lock dbus interface!')
            return RC_FAILED_LOCKING_API

        num_leds = self.iface.get_num_leds()
        vf = self.constant([LED_KANO_ORANGE for i in range(num_leds)])
        duration = update_rate
        cycles = duration / 2

        while not self.interrupted:
            if self.iface.is_speaker_plugged():  # TODO: rename method to is_plugged

                led_speeds = self._get_cpu_led_speeds(0.1, num_leds)

                vf2 = self.pulse_each(vf, led_speeds)
                successful = self.animate(vf2, duration, cycles)

                if not successful:
                    time.sleep(duration)
            else:
                time.sleep(duration)

        if not self.iface.unlock():
            logger.warn('LED Ring: CpuMonitor: Could not unlock dbus interface!')

    def stop(self):
        """
        """
        super(CpuMonitor, self).stop('cpu-monitor')

    def _get_cpu_monitor_setting(self):
        return get_setting('LED-Speaker-anim')

    def _get_cpu_led_speeds(self, speed_scale, num_leds):
        # get the top NUM_LEDS processes by CPU usage - PID, %CPU
        cmd = 'ps -eo pid,pcpu --no-headers --sort -pcpu | head -n {}'.format(num_leds)
        output, error, _ = run_cmd(cmd)

        if error:
            logger.error('_get_cpu_led_speeds: cmd error - [{}]'.format(error))
            sys.exit(RC_FAILED_CPU_MONIT_FETCH)

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
            sys.exit(RC_FAILED_CPU_MONIT_FETCH)
