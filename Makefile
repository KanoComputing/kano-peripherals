# Makefile
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# Standard interface to work with the project.


.PHONY: clean docs libs

clean:
	cd docs && make clean

docs:
	cd docs && make all

libs:
	cd libs/pi_hat && cmake . && make
