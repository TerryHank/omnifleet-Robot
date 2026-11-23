# OmniFleet A2 deployment

These deployment files were captured from `/home/iecme/omnifleet_a2_ws`. The public repository uses branch `A2`. For the captured Fast DDS services and restore commands, see the [124 runtime guide](../../runtime_124/README.md).

The original cutover procedure was to install the files in `systemd/`, copy the
production values to `/etc/omnifleet_a2/robot.env`, disable the replaced
legacy units, then enable the five `omnifleet-a2-*` units. Do not cut over the
chassis service until the matching STM32 communication-loss watchdog firmware
has been flashed and verified.
