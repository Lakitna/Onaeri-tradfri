"""
Tradfri wrapper for Onaeri API
https://github.com/Lakitna/Onaeri-tradfri
"""

__version__ = '0.5'


print("\n" * 100)
print("Onaeri Tradfri v%s" % __version__)


from Onaeri import Onaeri, settings
import control
import com
import lampdata
from time import sleep


onaeri = Onaeri( settings, lampdata.now() )
print("\n--------------------------------------------------\n")



def heartbeat(position=True):
    """
    Display network heartbeat
    """
    if position:
        print("\033[1;31m♥\033[0;0m", end="", flush=True)
        return
    else:
        print("\b ", end="", flush=True)
        print("\b", end="")
        return


while True:
    heartbeat(True)
    lampData = lampdata.now()
    heartbeat(False)

    # Progress all cycles and pass the current state of all lamps
    onaeri.tick( lampData )

    if onaeri.update:
        print("[%s] Update called:" % (onaeri.time.timeStamp))
        for cycle in onaeri.cycles:
            if not cycle.lamp.isEmpty():
                print('\t%s: %s' % (cycle.name, cycle.lamp))


        heartbeat(True)
        control.color( onaeri )
        control.brightness( onaeri )
        control.power( onaeri )
        heartbeat(False)


    # Slow down a bit, no stress brah
    try:
        sleep( settings.Global.mainLoopDelay )
    except KeyboardInterrupt:
        print("\nKeyboard interrupt. Exiting.")
        exit()
