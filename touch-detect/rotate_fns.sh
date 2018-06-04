# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# functions to support  screen flipping


function is_rotated() {
    # NB this command requires a vhci slot to run. Therefore it must
    # not be run at arbitrary times, only when we are certain that we don't need all the
    # slots

    vcgencmd get_config display_rotate |grep 2
}

function exitStatus {
    # return first arg as exit status
    ( exit $1 )
}


function setXorgRotation {
    if exitStatus $1 ; then
       TOUCH_DEVICES=$(touch-detect)
       for device in $TOUCH_DEVICES; do
           xinput set-prop $device 'libinput Calibration Matrix' -1.0 0.0 1.0 0.0 -1.0 1.0 0 0 1
       done
    fi
}

function setQtRotation {
    if exitStatus $1 ; then
       export QT_QPA_LIBINPUT_TOUCH_MATRIX="-1 0 1 0 -1 1"
    else
       unset QT_QPA_LIBINPUT_TOUCH_MATRIX
       export -n QT_QPA_LIBINPUT_TOUCH_MATRIX
    fi

}

function exportQtRotation {
    systemctl --user import-environment QT_QPA_LIBINPUT_TOUCH_MATRIX
}
