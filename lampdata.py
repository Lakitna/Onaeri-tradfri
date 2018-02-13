from com import light_objects, api
from pytradfri import error
from pytradfri.const import (
    RANGE_HUE, RANGE_SATURATION, RANGE_BRIGHTNESS, RANGE_MIREDS)
import threading
import time
from Onaeri.Onaeri import lamp, helper
from Onaeri.Onaeri.logger import log
from Onaeri.Onaeri.settings.Global import valRange

featureReference = {1: 'dim', 2: 'temp', 8: 'color'}
metrics = {'threads': [], 'thread stopped': 0, 'thread started': 0,
           'thread callback': 0, 'poll total': 0}
unreachable = []
threadList = []


class ObserverThread(threading.Thread):
    def __init__(self, threadID, device):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = "Thread-%d" % threadID
        self.daemon = True
        self.device = device
        self.logFile = "Thread-%s" % self.device.name

    def run(self):
        """Thread runtime"""
        while True:
            metrics['thread started'] += 1
            log.blind("[time] >>", self.logFile, end="")
            api(self.device.observe(self._callback,
                                    self._err_callback,
                                    duration=(1800 + self.threadID)))
            log.blind("<< [time]", self.logFile)
            time.sleep(.01)  # Stability delay

    def _callback(self, device):
        """Lamp change callback"""
        self.device = device
        metrics['thread callback'] += 1
        log.blind("!", self.logFile, end="")
        # print("Received message for: %s" % self.device)

    def _err_callback(self, err):
        """Observing stopped callback"""
        metrics['thread stopped'] += 1
        log.blind("X", self.logFile, end="")


def setup():
    """
    Setup observing threads and return the first lampData
    """
    log("Subscribing to lamp changes: ", end="", flush=True)
    for i in range(len(light_objects)):
        thread = ObserverThread(i, light_objects[i])
        thread.start()

        threadList.append(thread)
        metrics['threads'].append(thread.device.name)
        time.sleep(0.2)  # Stability delay

    log.success("Done")
    log()
    return poll(True)


def _defineFeatures(light):
    """
    Restructure features to Onaeri specs
    """
    ret = {}
    for f in featureReference:
        if light.supported_features & f:
            ret[featureReference[f]] = True
        else:
            ret[featureReference[f]] = False
    return ret


def poll(first=False):
    """
    Get info from all lamps from gateway.
    """
    if len(threadList) != len(light_objects):
        log.warn("[lampData] Threadcount discrepancy: %s"
                 % {"threads": len(threadList), "lamps": len(light_objects)})

    metrics['poll total'] += 1
    ret = []
    for thread in threadList:
        device = thread.device
        light = device.light_control.lights[0]

        power = False
        if device.reachable:
            if device.name in unreachable:
                unreachable.remove(device.name)
            power = light.state
        else:
            if device.name not in unreachable:
                unreachable.append(device.name)
                log.warn("Unreachable devices: %s" % unreachable)

        if first:
            features = _defineFeatures(light)
        else:
            features = None

        hue = helper.scale(light.hsb_xy_color[0],
                           RANGE_HUE,
                           valRange)
        saturation = helper.scale(light.hsb_xy_color[1],
                                  RANGE_SATURATION,
                                  valRange)
        brightness = helper.scale(light.dimmer,
                                  RANGE_BRIGHTNESS,
                                  valRange)
        colorTemp = helper.scale(light.color_temp,
                                 (RANGE_MIREDS[1], RANGE_MIREDS[0]),
                                 valRange)

        ret.append(lamp.Lamp(
                   brightness=brightness,
                   color=colorTemp,
                   power=power,
                   name=device.name,
                   features=features,
                   hue=hue,
                   sat=saturation))

    return ret
