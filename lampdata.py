from Onaeri.lamp import Lamp
from Onaeri import helper
from Onaeri.logger import log
from Onaeri.settings.Global import valRange
from com import light_objects, api
from pytradfri import error


briRange = (1, 254)
colorRange = (454, 250)
hueRange = (0, 65535)
satRange = (0, 65279)
satCorrect = (626, 347)
featureReference = {1: 'dim', 2: 'temp', 8: 'color'}
metrics = {'total': 0, 'success': 0, 'timeout': 0}
unreachable = []


def _defineFeatures(light):
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
    metrics['total'] += 1
    ret = []
    for device in light_objects:
        try:
            command = device.update()
            command._timeout = 3
            api(command)
        except error.RequestTimeout:
            print("×")
            metrics['timeout'] += 1
            return None

        try:
            light = device.light_control.lights[0]
        except TypeError:
            log.error("A lamp has been removed from the network")

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

    metrics['success'] += 1
    return ret
