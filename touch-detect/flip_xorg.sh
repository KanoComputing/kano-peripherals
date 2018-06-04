#!/bin/bash
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# flip_xorg.sh
#

.  /usr/share/kano-peripherals/scripts/rotate_fns.sh

is_rotated; IS_ROTATED=$?
setXorgRotation $IS_ROTATED

