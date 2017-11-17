"""
Tradfri wrapper for Onaeri API
https://github.com/Lakitna/Onaeri-tradfri
"""

__version__ = '0.6.0'


print("\n" * 100)

from Onaeri.logger import *

log("Onaeri Tradfri v%s\n" % __version__)

from Onaeri import Onaeri, settings
import control
import com
import lampdata
from time import sleep


onaeri = Onaeri( lampdata.now() )
log("\n--------------------------------------------------\n")


def heartbeat(state=True):
    """
    Display network heartbeat
    """
    if state:
        print("\033[1;31m♥\033[0;0m\b", end="", flush=True)
        return
    else:
        print(" \b", end="", flush=True)
        return

while True:
    try:
        heartbeat(True)
        lampData = lampdata.now()
        heartbeat(False)

        # Progress all cycles and pass the current state of all lamps
        onaeri.tick( lampData )

        if onaeri.update:
            log("[%s]:" % (onaeri.time.timeStamp))
            for cycle in onaeri.cycles:
                if not cycle.lamp.isEmpty():
                    log('\t%s: %s' % (cycle.name, cycle.lamp))

            heartbeat(True)
            control.color( onaeri )
            control.brightness( onaeri )
            control.power( onaeri )
            heartbeat(False)

        # Slow down a bit, no stress brah
        sleep( settings.Global.mainLoopDelay )
    except KeyboardInterrupt:
        log()
        log("Keyboard interrupt. Exiting.")
        exit()
