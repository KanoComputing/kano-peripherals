# NB no shebang because this script must be sourced
#
# set_rotate.sh
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
#


function is_rotated() {

    vcgencmd get_config display_rotate |grep 2
}

if is_rotated; then
   export QT_QPA_LIBINPUT_TOUCH_MATRIX="-1 0 1 0 -1 1"
   TOUCH_DEVICES=$(touch-detect)
   for device in $TOUCH_DEVICES; do
       xinput set-prop $device 'libinput Calibration Matrix' -1.0 0.0 1.0 0.0 -1.0 1.0 0 0 1
   done
else
   unset QT_QPA_LIBINPUT_TOUCH_MATRIX
   export -n QT_QPA_LIBINPUT_TOUCH_MATRIX
fi
