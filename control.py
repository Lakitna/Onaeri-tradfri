from sys import exc_info
import time

from pytradfri import error
import com
import Onaeri.settings as settings
from Onaeri import data, helper
from Onaeri.logger import log
from lampdata import briRange, colorRange, hueRange, satRange, satCorrect

metrics = {'brightness': 0, 'color': 0, 'sat': 0, 'power': 0,
           'timeout': 0, 'total': 0}


def power(api):
    """
    Turn one or more lamps in one or more cycles on or off.
    """
    def set(cycle, id):
        lamp = com.light_ids[id]
        command = lamp.light_control.set_state(cycle.lamp[id].power)
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
        time.sleep(settings.Global.transitionTime)


def color(api):
    """
    Update the color of one or more lamps in one or more cycles.
    """
    def set_temp(cycle, id):
        val = helper.scale(cycle.lamp[id].color,
                           settings.Global.valRange,
                           colorRange)
        lamp = com.light_ids[id]
        command = lamp.light_control.set_color_temp(
            val,
            transition_time=settings.Global.transitionTime * 10
        )
        _sendCommand(command)
        metrics['color'] += 1

    def set_color(cycle, id):
        h = helper.scale(90,
                         settings.Global.valRange,
                         hueRange)
        s = helper.scale(cycle.lamp[id].color,
                         settings.Global.valRange,
                         satCorrect)
        s = helper.scale(s,
                         settings.Global.valRange,
                         satRange)
        s = helper.limitTo(s, satRange)
        b = helper.scale(cycle.lamp[id].brightness,
                         settings.Global.valRange,
                         briRange)

        lamp = com.light_ids[id]
        command = lamp.light_control.set_hsb(
            h, s, b,
            transition_time=settings.Global.transitionTime * 10
        )
        _sendCommand(command)
        metrics['color'] += 1

    def set_hsb(cycle, id):
        h = helper.scale(cycle.lamp[id].hue,
                         settings.Global.valRange,
                         hueRange)
        s = helper.scale(cycle.lamp[id].sat,
                         settings.Global.valRange,
                         satRange)
        b = helper.scale(cycle.lamp[id].brightness,
                         settings.Global.valRange,
                         briRange)

        lamp = com.light_ids[id]
        command = lamp.light_control.set_hsb(
            h, s, b,
            transition_time=settings.Global.transitionTime * 10
        )
        _sendCommand(command)
        metrics['color'] += 1

    update = False
    for cycle in api.cycles:
        if cycle.update:
            for id in cycle.lamp:
                if cycle.lamp[id].color is not None:
                    if cycle.lamp[id].features['temp'] is True:
                        set_temp(cycle, id)
                    if cycle.lamp[id].features['color'] is True:
                        set_color(cycle, id)
                    update = True
                elif (cycle.lamp[id].hue is not None
                      and cycle.lamp[id].sat is not None):
                    set_hsb(cycle, id)
                    update = True
    if update:
        time.sleep(settings.Global.transitionTime)


def hsb(api):
    """
    Update the saturation of one or more lamps in one or more cycles.
    """
    def set(cycle, id):
        h = helper.scale(cycle.lamp[id].hue,
                         settings.Global.valRange,
                         hueRange)
        s = helper.scale(cycle.lamp[id].sat,
                         settings.Global.valRange,
                         satRange)
        b = helper.scale(cycle.lamp[id].brightness,
                         settings.Global.valRange,
                         briRange)
        lamp = com.light_ids[id]
        command = lamp.light_control.set_hsb(
            h, s, b,
            transition_time=settings.Global.transitionTime * 10
        )
        _sendCommand(command)
        metrics['sat'] += 1

    update = False
    for cycle in api.cycles:
        if cycle.update:
            for id in cycle.lamp:
                if cycle.lamp[id].sat is not None:
                    set(cycle, id)
                    update = True
    if update:
        time.sleep(settings.Global.transitionTime)


def brightness(api):
    """
    Update the brightness of one or more lamps in one or more cycles.
    """
    def set(cycle, id):
        val = helper.scale(cycle.lamp[id].brightness,
                           settings.Global.valRange,
                           briRange)
        lamp = com.light_ids[id]
        command = lamp.light_control.set_dimmer(
            val,
            transition_time=settings.Global.transitionTime * 10
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
        time.sleep(settings.Global.transitionTime)


def _sendCommand(command, iteration=1):
    """
    Send command with retry on timeout
    """
    try:
        com.api(command)
        metrics['total'] += 1
    except error.RequestTimeout:
        log.warn("[Control] Timeout error on try %d" % iteration)
        metrics['timeout'] += 1
        if iteration < settings.Global.commandsTries:
            _sendCommand(command, iteration=iteration + 1)
