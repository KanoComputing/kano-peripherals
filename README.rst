kano-peripherals
----------------

Support code for peripherals (initially, speaker LEDs).


battery-status
--------------

A tool that detects if the battery is connected and if the charge is too
low, to power off the kit. See the file ``bin/kano-boot-battery`` for
details.

WARNING

-  APIs are considered unstable for the Kano OS 2.1 release.

This is because we may want to introduce a daemon, and the design of
this will influence the API. Currently the API requires root, but this
won't be necessary if we have a daemon.

Access should be via the kano-speakerleds binary.


Testing Low Battery on boot
---------------------------

This module will turn off the kit automatically on boot if the battery
is too low. A warning message will be displayed on the console, and
afterwards the kit will turn itself off.

There are 3 ways to test this functionality:

-  Letting the battery run low, which is not practical most times
-  Interactively from a terminal, with
   ``sudo kano-boot-battery --dry-run``, no reboot will take place
-  Faking low battery signal with
   ``sudo kano-boot-battery --enable-test && sudo reboot``

When faking the low battery signal, it should run the test on next
reboot and then return to normal boot to Dashboard.
