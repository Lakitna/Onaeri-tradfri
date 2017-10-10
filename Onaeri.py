#!/usr/bin/env python3
"""
Awesome Tradfri controller for circadian rhythm improvement

Source:
https://github.com/Lakitna/Onaeri-tradfri

To run execute command:
$ python3 Onaeri.py
"""


__version__ = '0.1'
__author__ = 'Sander van Beek'


# Clear terminal
print("\n" * 100)
print("Onaeri Tradfri v%s" % __version__)
print()


from time import sleep
from timecode import TimeCode
from cycle import Cycle




###########
## SETUP ##
###########
# Timecode class setup
tc = TimeCode()

# Setup the cycles
cycleA = Cycle([0])
cycleB = Cycle([1], wakeTime=(6,30), sleepTime=(22,0))



##########
## LOOP ##
##########
while True:
    # Tick timecode
    tc.tick()

    # Tick cycles
    cycleA.tick( tc )
    cycleB.tick( tc )

    # Slow down a bit, no stress brah
    sleep(1)


    # Temporary api documentation
    # Print all lights
    # print(lights)

    # Lights can be accessed by its index, so lights[1] is the second light
    # light = lights[0]

    # print()
    # print("Name: ", light.name)
    # print("State: ", light.light_control.lights[0].state)
    # print("Dimmer level: ", light.light_control.lights[0].dimmer)
    # print()
