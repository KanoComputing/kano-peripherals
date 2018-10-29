# Makefile
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# Standard interface to work with the project.

REPO:= kano-peripherals

.PHONY: clean docs libs touch-detect

clean:
	cd docs && make clean

docs:
	cd docs && make all

libs:
	cd libs/pi_hat && cmake . && make

touch-detect:
	cd touch-detect && make release
	cd touch-detect && make debug

#
# Add test targets
#
include pythontest.mk
check: pythontest
test: check
