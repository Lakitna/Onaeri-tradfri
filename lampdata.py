from Onaeri.lamp import Lamp
from Onaeri import helper
from Onaeri.logger import log
from Onaeri.settings.Global import valRange
from com import light_objects, api
from pytradfri import error


briRange = (1, 254)
colorRange = (454, 250)
metrics = {'total': 0, 'success': 0, 'timeout': 0}
unreachable = []


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
            features = light.supported_features
        else:
            features = None

        ret.append(Lamp(
                   helper.scale(light.dimmer, briRange, valRange),
                   helper.scale(light.color_temp, colorRange, valRange),
                   power,
                   name=device.name,
                   features=features
                   ))

    metrics['success'] += 1
    return ret
