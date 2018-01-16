from Onaeri.lamp import Lamp
from Onaeri import helper
from Onaeri.logger import log
from Onaeri.settings.Global import valRange
from com import light_objects, api
from pytradfri import error
import threading
import time


briRange = (1, 254)
colorRange = (454, 250)
hueRange = (0, 65535)
satRange = (0, 65279)
satCorrect = (626, 347)
featureReference = {1: 'dim', 2: 'temp', 8: 'color'}
metrics = {'threads': [], 'thread_stopped': 0, 'thread_started': 0,
           'thread_callback': 0, 'poll_total': 0}
unreachable = []
threadList = []


class ObserverThread(threading.Thread):
    def __init__(self, threadID, device):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = "Thread-%d" % threadID
        self.daemon = True
        self.device = device

    def run(self):
        """
        Thread runtime
        """
        while True:
            metrics['thread_started'] += 1
            api(self.device.observe(self._callback,
                                    self._err_callback,
                                    duration=3600))
            time.sleep(.01)  # Stability delay

    def _callback(self, device):
        """Lamp change callback"""
        self.device = device
        metrics['thread_callback'] += 1
        # print("Received message for: %s" % self.device)

    def _err_callback(self, err):
        """Observing stopped callback"""
        metrics['thread_stopped'] += 1


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
        time.sleep(0.2)

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

    metrics['poll_total'] += 1
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

        saturation = helper.scale(light.hsb_xy_color[1], satRange, valRange)
        colorTemp = helper.scale(light.color_temp, colorRange, valRange)
        if colorTemp is None:
            if helper.inRange(saturation, satCorrect):
                colorTemp = helper.scale(saturation, satCorrect, valRange)

        ret.append(Lamp(
                   helper.scale(light.dimmer, briRange, valRange),
                   colorTemp,
                   power,
                   name=device.name,
                   features=features,
                   hue=helper.scale(light.hsb_xy_color[0], hueRange, valRange),
                   sat=saturation,
                   ))

    return ret
