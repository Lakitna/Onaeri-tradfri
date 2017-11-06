from onaeri.lamp import Lamp
from onaeri.helper import printWarning
from com import light_objects, api
from pytradfri import error


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
            printWarning("\b×")
            return None

        light = device.light_control.lights[0]

        power = False
        if device.reachable:  power = light.state

        ret.append( Lamp(light.dimmer, light.kelvin_color_inferred, power, name=lamp.name) )
    return ret
