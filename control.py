from sys import exc_info
import time

from pytradfri import error
from pytradfri.const import (
    RANGE_HUE, RANGE_SATURATION, RANGE_BRIGHTNESS,
    RANGE_MIREDS, RANGE_X, RANGE_Y)
from com import light_ids, api
from Onaeri.settings.Global import valRange, transitionTime
from Onaeri.helper import scale
from Onaeri.logger import log

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
        val = scale(cycle.lamp[id].color, valRange, RANGE_MIREDS)
        command = light_ids[id].light_control.set_color_temp(
            val,
            transition_time=transitionTime * 10
        )
        _sendCommand(command)
        metrics['color'] += 1

    def set_color(cycle, id):
        """Color bulb, set color temperature"""
        mired = scale(cycle.lamp[id].color, valRange, RANGE_MIREDS)
        xy = _miredToXY(mired)
        x = scale(xy[0], (0, 1), RANGE_X)
        y = scale(xy[1], (0, 1), RANGE_Y)
        command = light_ids[id].light_control.set_xy_color(
            x, y,
            transition_time=transitionTime * 10
        )
        _sendCommand(command)
        metrics['color'] += 1

    def set_hsb(cycle, id):
        """Color bulb, set color"""
        h = scale(cycle.lamp[id].hue, valRange, RANGE_HUE)
        s = scale(cycle.lamp[id].sat, valRange, RANGE_SATURATION)
        b = scale(cycle.lamp[id].brightness, valRange, RANGE_BRIGHTNESS)
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
        val = scale(cycle.lamp[id].brightness, valRange, RANGE_BRIGHTNESS)
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
        if iteration < settings.Global.commandsTries:
            _sendCommand(command, iteration=iteration + 1)
