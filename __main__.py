"""
Tradfri wrapper for Onaeri API
https://github.com/Lakitna/Onaeri-tradfri
"""

__version__ = '0.8.0'

import traceback
import atexit
from time import sleep, strftime
import control
import lampdata
from Onaeri.Onaeri.logger import log
from Onaeri.Onaeri import Onaeri, settings, __version__ as onaeriVersion

onaeri = Onaeri(lampdata.setup())
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
            return "%s%% #superLow" % val
        if val < 90:
            return "%s%% #low" % val
        if val < 95:
            return "%s%% #ok" % val
        if val > 98:
            return "%s%% #awesome" % val
        if val >= 95:
            return "%s%% #good" % val
        return val

    version = {}
    version['Onaeri API'] = onaeriVersion
    version['Onaeri Tradfri'] = __version__

    time = {}
    time['timecodes'] = onaeri.time.runtime
    time['minutes'] = round(onaeri.time.runtime
                            * settings.Global.minPerTimeCode, 2)
    time['hours'] = round((onaeri.time.runtime
                          * settings.Global.minPerTimeCode) / 60, 2)

    observer = lampdata.metrics
    observer['thread count'] = len(observer['threads'])

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
onaeri.scheduler.add((23, 59), summaryBuild, "Daily runtime summary")


def heartbeat(state=True):
    """
    Display network heartbeat
    """
    if state:
        print("\033[1;31m♥\033[0;0m\b", end="", flush=True)
    else:
        print(" \b", end="", flush=True)
    return


while True:
    try:
        lampData = lampdata.poll()

        # Progress all cycles and pass the current state of all lamps
        onaeri.tick(lampData)

        if onaeri.update:
            updateCounter += 1
            print("[%s]:" % (strftime("%H:%M:%S")))

            for cycle in onaeri.cycles:
                for id in cycle.lamp:
                    if not cycle.lamp[id].isEmpty(['brightness', 'color',
                                                   'power', 'hue', 'sat']):
                        print("\t%s: %s" % (id, cycle.lamp[id]))

            heartbeat(True)
            control.color(onaeri)
            control.brightness(onaeri)
            control.power(onaeri)
            heartbeat(False)

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
