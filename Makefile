# Makefile
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# Standard interface to work with the project.


.PHONY: clean docs


clean:
	cd docs && make clean

docs:
	cd docs && make all
