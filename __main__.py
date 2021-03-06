"""
Tradfri wrapper for Onaeri API
https://github.com/Lakitna/Onaeri-tradfri
"""

__version__ = '0.8.0'

import sys
import os
import traceback
import atexit
from time import sleep, strftime
from Onaeri.logger import log
from Onaeri import Onaeri, settings, __version__ as onaeriVersion
import control
import lampdata

onaeri = Onaeri(lampdata.poll())
restartTime = onaeri.time.code((3, 0), dry=True)
updateCounter = 0

log()
log.row()
log("RUNTIME STARTED")
log("Onaeri v%s" % (onaeriVersion))
log("Onaeri Tradfri v%s" % __version__)
log.row()
log()


def summaryBuild():
    def colorSuccessRate(val):
        if val < 80:
            return "%s #superLow" % val
        if val < 90:
            return "%s #low" % val
        if val < 95:
            return "%s #ok" % val
        if val > 98:
            return "%s #awesome" % val
        if val >= 95:
            return "%s #good" % val
        return val

    version = {}
    import Onaeri
    version['Onaeri API'] = Onaeri.__version__
    version['Onaeri Tradfri'] = __version__

    time = {}
    time['timecodes'] = onaeri.time.runtime
    time['minutes'] = round(onaeri.time.runtime
                            * settings.Global.minPerTimeCode, 2)
    time['hours'] = round((onaeri.time.runtime
                          * settings.Global.minPerTimeCode) / 60, 2)

    observer = lampdata.metrics
    observer["success rate"] = round((observer['success']
                                     / observer['total']) * 100, 2)
    observer['success rate'] = colorSuccessRate(observer['success rate'])

    ctrl = control.metrics
    try:
        ctrl['success rate'] = round(((ctrl['total'] - ctrl['timeout'])
                                     / ctrl['total']) * 100, 2)
        ctrl['success rate'] = colorSuccessRate(ctrl['success rate'])
    except ZeroDivisionError:
        ctrl['success rate'] = None

    log.summary({
        'Versions': version,
        'Program runtime': time,
        'Observer calls': observer,
        'Lamp changes made': ctrl,
        'Updates handled': updateCounter,
        'Cycles handled': [cycle.name for cycle in onaeri.cycles],
    })


atexit.register(summaryBuild)


def restart():
    """
    Restart entire program if the time is right
    """
    if onaeri.time.latestCode == restartTime and onaeri.time.runtime > 0:
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
        lampData = lampdata.poll()
        heartbeat(False)

        # Progress all cycles and pass the current state of all lamps
        onaeri.tick(lampData)

        if onaeri.update:
            updateCounter += 1
            print("[%s]:" % (strftime("%H:%M:%S")))

            for cycle in onaeri.cycles:
                for id in cycle.lamp:
                    if not cycle.lamp[id].isEmpty(['brightness',
                                                   'color',
                                                   'power']):
                        print("\t%s: %s" % (cycle.name, cycle.lamp[id]))

            heartbeat(True)
            control.color(onaeri)
            control.brightness(onaeri)
            control.power(onaeri)
            heartbeat(False)

        restart()

        # Slow down a bit, no stress brah
        sleep(settings.Global.mainLoopDelay)
    except KeyboardInterrupt:
        log()
        log("Keyboard interrupt. Exiting.")
        exit()
    except Exception:
        log()
        log("An error occurred:")
        log(traceback.format_exc())
        exit()
