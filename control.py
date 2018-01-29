from sys import exc_info
import time
from pytradfri import error
from pytradfri.const import (
    RANGE_HUE, RANGE_SATURATION, RANGE_BRIGHTNESS,
    RANGE_MIREDS, RANGE_X, RANGE_Y)
from com import light_ids, api
from Onaeri.Onaeri import helper
from Onaeri.Onaeri.logger import log
from Onaeri.Onaeri.settings.Global import (
    valRange, transitionTime, commandsTries)

metrics = {'brightness': 0, 'color': 0, 'sat': 0, 'power': 0,
           'timeout': 0, 'total': 0}

# Reverse range
RANGE_MIREDS = (RANGE_MIREDS[1], RANGE_MIREDS[0])


def power(api):
    """
    Turn one or more lamps in one or more cycles on or off.
    """
    def set(cycle, id):
        command = light_ids[id].light_control.set_state(cycle.lamp[id].power)
        _sendCommand(command)
        metrics['power'] += 1

    update = False
    for cycle in api.cycles:
        if cycle.update:
            for id in cycle.lamp:
                if cycle.lamp[id].power is not None:
                    set(cycle, id)
                    update = True
    if update:
        time.sleep(transitionTime)


def color(api):
    """
    Update the color of one or more lamps in one or more cycles.
    """
    def set_temp(cycle, id):
        """White spectrum bulb"""
        val = helper.scale(cycle.lamp[id].color, valRange, RANGE_MIREDS)
        command = light_ids[id].light_control.set_color_temp(
            val,
            transition_time=transitionTime * 10
        )
        _sendCommand(command)
        metrics['color'] += 1

    def set_color(cycle, id):
        """Color bulb, set color temperature"""
        mired = helper.scale(cycle.lamp[id].color, valRange, RANGE_MIREDS)
        xy = _miredToXY(mired)
        x = helper.scale(xy[0], (0, 1), RANGE_X)
        y = helper.scale(xy[1], (0, 1), RANGE_Y)
        command = light_ids[id].light_control.set_xy_color(
            x, y,
            transition_time=transitionTime * 10
        )
        _sendCommand(command)
        metrics['color'] += 1

    def set_hsb(cycle, id):
        """Color bulb, set color"""
        h = helper.scale(cycle.lamp[id].hue, valRange, RANGE_HUE)
        s = helper.scale(cycle.lamp[id].sat, valRange, RANGE_SATURATION)
        b = helper.scale(cycle.lamp[id].brightness, valRange, RANGE_BRIGHTNESS)
        command = light_ids[id].light_control.set_hsb(
            h, s, b,
            transition_time=transitionTime * 10
        )
        _sendCommand(command)
        metrics['color'] += 1

    update = False
    for cycle in api.cycles:
        if cycle.update:
            for id in cycle.lamp:
                lamp = cycle.lamp[id]
                if lamp.color is not None:
                    if lamp.features['temp'] is True:
                        # White spectrum bulb
                        set_temp(cycle, id)
                        update = True
                    if lamp.features['color'] is True:
                        # Color bulb, set color temp
                        set_color(cycle, id)
                        update = True
                elif lamp.hue is not None and lamp.sat is not None:
                    # Color bulb, set color
                    set_hsb(cycle, id)
                    update = True
    if update:
        time.sleep(transitionTime)


def brightness(api):
    """
    Update the brightness of one or more lamps in one or more cycles.
    """
    def set(cycle, id):
        val = helper.scale(cycle.lamp[id].brightness,
                           valRange,
                           RANGE_BRIGHTNESS)
        command = light_ids[id].light_control.set_dimmer(
            val,
            transition_time=transitionTime * 10
        )
        _sendCommand(command)
        metrics['brightness'] += 1

    update = False
    for cycle in api.cycles:
        if cycle.update:
            for id in cycle.lamp:
                if cycle.lamp[id].brightness is not None:
                    set(cycle, id)
                    update = True
    if update:
        time.sleep(transitionTime)


def _sendCommand(command, iteration=1):
    """
    Send command with retry on timeout
    """
    try:
        api(command)
        metrics['total'] += 1
    except error.RequestTimeout:
        log.warn("[Control] Timeout error on try %d" % iteration)
        metrics['timeout'] += 1
        if iteration < commandsTries:
            _sendCommand(command, iteration=iteration + 1)


def _miredToXY(mired):
    """
    Planckian locus approximation function
    http://en.wikipedia.org/wiki/Planckian_locus#Approximation
    """
    # Mired to kelvin
    T = float(1000000 / mired)

    if 1667 <= T <= 4000:
        x = (-0.2661239 * (10**9 / T**3) - 0.2343580 * (10**6 / T**2)
             + 0.8776956 * (10**3 / T) + 0.179910)
    elif 4000 <= T <= 25000:
        x = (-3.0258469 * (10**9 / T**3) + 2.107379 * (10**6 / T**2)
             + 0.2226347 * (10**3 / T) + 0.240390)
    else:
        raise ValueError("T out of range")

    if 1667 <= T <= 2222:
        y = (-1.1063814 * x**3 - 1.34811020 * x**2
             + 2.18555832 * x - 0.20219683)
    elif 2222 <= T <= 4000:
        y = (-0.9549476 * x**3 - 1.37418593 * x**2
             + 2.09137015 * x - 0.16748867)
    elif 4000 <= T <= 25000:
        y = (3.0817580 * x**3 - 5.87338670 * x**2
             + 3.75112997 * x - 0.37001483)
    else:
        raise ValueError("T out of range")

    return (x, y)
