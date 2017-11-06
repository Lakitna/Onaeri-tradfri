
__version__ = '0.3'
__author__ = 'Sander van Beek'


print("\n" * 100)
print("Onaeri Tradfri v%s" % __version__)

from onaeri import Onaeri


import settings
import control
import com
import lampdata
from time import sleep


onaeri = Onaeri( settings, lampdata.now() )
print("\nNow active\n")



def heartbeat(position="high"):
    if position == "high":
        print("\b♥", end="", flush=True)
        return
    if position == "low":
        print("\b ", end="", flush=True)
        print("\b", end="")
        return



while True:
    # Display network heartbeat
    heartbeat("high")
    lampData = lampdata.now()
    heartbeat("low")

    # Progress all cycles and pass the current state of all lamps
    onaeri.tick( lampData )

    if onaeri.update:
        print("[%s] Update called:" % (onaeri.time.timeStamp))
        for cycle in onaeri.cycles:
            if not cycle.lamp.isEmpty():
                print('\t%s: %s' % (cycle.name, cycle.lamp))


        heartbeat("high")
        control.color( onaeri )
        control.brightness( onaeri )
        control.power( onaeri )
        heartbeat("low")


    # Slow down a bit, no stress brah
    sleep( settings.Global.mainLoopDelay )
