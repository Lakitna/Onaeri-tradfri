from Onaeri.lamp import Lamp
from Onaeri.logger import *
from Onaeri import helper
from Onaeri.settings.Global import valRange
from com import light_objects, api
from pytradfri import error


briRange         = (1, 254)   # [min, max] brightness. Unsigned int
colorRange       = (454, 250) # [min, max] color temp. Unsigned int


def now():
    """
    Get info from all lamps from gateway.
    """
    ret = []
    for lamp in light_objects:
        device = lamp

        try:
            api(device.update())
        except error.RequestTimeout:
            print("\b", end="")
            logWarn("×")
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
    return ret
