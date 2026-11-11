# OmniFleet A2 deployment

The production source of truth is `/home/iecme/omnifleet_a2_ws` on branch
`main`. Runtime state and maps stay outside the repository.

The service cutover is atomic: install the files in `systemd/`, copy the
production values to `/etc/omnifleet_a2/robot.env`, disable the replaced
legacy units, then enable the five `omnifleet-a2-*` units. Do not cut over the
chassis service until the matching STM32 communication-loss watchdog firmware
has been flashed and verified.
