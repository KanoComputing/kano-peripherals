# kano-peripherals
Support code for peripherals (initially, speaker LEDs)


WARNING

 * APIs are considered unstable for the Kano OS 2.1 release.
 
This is because we may want to introduce a daemon, and the design of this will influence the API.
Currently the API requires root, but this won't be necessary if we have a daemon.

Access should be via the kano-speakerleds binary.