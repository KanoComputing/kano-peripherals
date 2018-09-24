#!/bin/bash
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# set_rotate.sh
#

.  /usr/share/kano-peripherals/scripts/rotate_fns.sh

is_rotated; IS_ROTATED=$?
setQtRotation  $IS_ROTATED
exportQtRotation
