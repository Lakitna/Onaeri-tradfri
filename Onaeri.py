#!/usr/bin/env python3
"""
Awesome Tradfri controller for circadian rhythm improvement

$ python3 Onaeri.py <IP> <KEY>
Where <IP> is the address to your IKEA gateway and
<KEY> is found on the back of your IKEA gateway.
"""


__version__ = '0.0'
__author__ = 'Sander van Beek'


# Clear terminal
print("\n" * 100)


# Standard modules
import time

# Custom modules
import settings
import com
import control
from timecode import TimeCode
from lookup import Lookup
from observer import Observer





###########
## SETUP ##
###########
# Lookup class setup
data = Lookup()


# exit()


# Timecode class setup
tc = TimeCode(minPerTimeCode=settings.minPerTimeCode)
# Observer class setup for lamp 0
obs = Observer(0)

# Make list to keep track of value changes
prevVals = [999,999]

##########
## LOOP ##
##########
while True:
    obs.do()

    # Print all lights
    # print(lights)

    # Lights can be accessed by its index, so lights[1] is the second light
    # light = lights[0]

    # print()
    # print("Name: ", light.name)
    # print("State: ", light.light_control.lights[0].state)
    # print("Dimmer level: ", light.light_control.lights[0].dimmer)
    # print()


    # If new timecode or observer dictates update
    if tc.update() or obs.update:
        # Only set lamp state on timecode update flag to enable manually
        # turning the lamps back on after auto-change.
        if not obs.update:
             data.setState( tc.get() )

        # Get new data from Lookup class
        vals = data.get( tc.get() )

        # If the vals have changed or observer dictates update
        if not vals == prevVals or obs.update:
            print("%s\t| bri: %d\t | color: %d" % (tc.decode(), vals[0], vals[1]))
            # Change color
            control.color(settings.colorValues[ vals[1] ] )
            # Change brightness
            control.brightness( vals[0] )


        # Prep for next loop
        prevVals = vals
        obs.update = False


    # Slow down a bit, no stress brah
    time.sleep(1)
