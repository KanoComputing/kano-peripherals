#
# paths.py
#
# Copyright (C) 2017-2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Adds the paths for the local libraries when operating from repo
#

import os
import sys

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..')
)
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__), '..', '..', '..', 'library', 'python'
    )
)
