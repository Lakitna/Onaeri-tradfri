#!/usr/bin/env python3
"""
Awesome Tradfri controller for circadian rhythm improvement

Source:
https://github.com/Lakitna/Onaeri-tradfri

To run execute command:
$ python3 Onaeri.py
"""


__version__ = '0.2'
__author__ = 'Sander van Beek'


# Clear terminal
print("\n" * 100)
print("Onaeri Tradfri v%s" % __version__)
print()


import time
from timekeeper import TimeKeeper
from cycle import Cycle
import settings




###########
## SETUP ##
###########
timeKeeper = TimeKeeper()

# Setup the cycles
cycles = []
for s in settings.app.cycles:
    cycles.append( Cycle(settingFile=s["settingFile"]) )


# Start message
print()
print("Onaeri is now active")
print()


##########
## LOOP ##
##########
while True:
    # Some monitoring stuff
    print("_", end="", flush=True)
    if timeKeeper.update:  print()


    # Tick stuff
    for cycle in cycles:
        cycle.tick( timeKeeper )

    timeKeeper.tick()

    # Slow down a bit, no stress brah
    time.sleep( settings.app.mainLoopDelay )
