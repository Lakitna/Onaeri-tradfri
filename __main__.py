"""
Tradfri wrapper for Onaeri API
https://github.com/Lakitna/Onaeri-tradfri
"""

__version__ = '0.6.2'


print("\n" * 100)

from Onaeri.logger import *

log("Onaeri Tradfri v%s\n" % __version__)

import sys, os
from Onaeri import Onaeri, settings
import control
import com
import lampdata
from time import sleep


onaeri = Onaeri( lampdata.now() )
log("\n--------------------------------------------------\n")


updateCounter = 0

def summaryBuild():
    version = {}
    import Onaeri
    version['Onaeri API'] = Onaeri.__version__
    version['Onaeri Tradfri'] = __version__

    time = {}
    time['timecodes'] = onaeri.time.runtime
    time['minutes'] = round(onaeri.time.runtime * settings.Global.minPerTimeCode, 2)
    time['hours'] = round((onaeri.time.runtime * settings.Global.minPerTimeCode) / 60, 2)

    observer = lampdata.count
    observer["success rate"] = round((observer['success'] / observer['total']) * 100, 2)

    ctrl = control.metrics
    try:
        ctrl['success rate'] = round(((ctrl['total']-ctrl['timeout']) / ctrl['total']) * 100, 2)
    except ZeroDivisionError:
        ctrl['success rate'] = None


    summary({
            'Versions': version,
            'Program runtime': time,
            'Observer calls': observer,
            'Lamp changes made': ctrl,
            'Updates handled': updateCounter,
            'Cycles handled': [cycle.name for cycle in onaeri.cycles],
        })

import atexit
atexit.register(summaryBuild)


restartTime = onaeri.time.makeCode((3,0), dry=True)
def restart():
    """
    Restart entire program if the time is right
    """
    if onaeri.time.timeCode == restartTime and onaeri.time.runtime > 0:
        summaryBuild()
        os.execl(sys.executable, sys.executable, *sys.argv)


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
            updateCounter += 1
            log("[%s]:" % (onaeri.time.timeStamp))
            for cycle in onaeri.cycles:
                for id in cycle.lamp:
                    if not cycle.lamp[id].isEmpty(['brightness', 'color', 'power']):
                        log('\t%s: %s' % (cycle.name, cycle.lamp[id]))

            heartbeat(True)
            control.color( onaeri )
            control.brightness( onaeri )
            control.power( onaeri )
            heartbeat(False)

        restart()

        # Slow down a bit, no stress brah
        sleep( settings.Global.mainLoopDelay )
    except KeyboardInterrupt:
        log()
        log("Keyboard interrupt. Exiting.")
        exit()
