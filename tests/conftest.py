#
# conftest.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The pytest conftest file
#
# Import fixtures and setup the tests
#

import os
import sys


# Add the path to the Python bindings for the board drivers
DRIVER_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'libs', 'pi_hat', 'library', 'python'
))
sys.path.insert(1, DRIVER_PATH)


from tests.fixtures.hw_config import *
