from Onaeri.lamp import Lamp
from Onaeri.logger import *
from Onaeri import helper
from Onaeri.settings.Global import valRange
from com import light_objects, api
from pytradfri import error


briRange         = (1, 254)   # [min, max] brightness. Unsigned int
colorRange       = (454, 250) # [min, max] color temp. Unsigned int
count = {'total': 0, 'success': 0, 'timeout': 0}

def now():
    """
    Get info from all lamps from gateway.
    """
    count['total'] += 1
    ret = []
    for lamp in light_objects:
        device = lamp

        try:
            api(device.update())
        except error.RequestTimeout:
            print("\b×")
            count['timeout'] += 1
            return None

        light = device.light_control.lights[0]

        power = False
        if device.reachable:  power = light.state

        ret.append( Lamp(
                helper.scale(light.dimmer,     briRange,   valRange),
                helper.scale(light.color_temp, colorRange, valRange),
                power,
                name=lamp.name)
            )
            
    count['success'] += 1
    return ret
