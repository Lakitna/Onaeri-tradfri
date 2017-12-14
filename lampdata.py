from Onaeri.lamp import Lamp
from Onaeri import helper
from Onaeri.settings.Global import valRange
from com import light_objects, api
from pytradfri import error


briRange = (1, 254)  # [min, max] brightness. Unsigned int
colorRange = (454, 250)  # [min, max] color temp. Unsigned int
metrics = {'total': 0, 'success': 0, 'timeout': 0}


def poll():
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

        light = device.light_control.lights[0]

        power = False
        if device.reachable:
            power = light.state

        ret.append(Lamp(
                   helper.scale(light.dimmer, briRange, valRange),
                   helper.scale(light.color_temp, colorRange, valRange),
                   power,
                   name=device.name)
                   )

    metrics['success'] += 1
    return ret
