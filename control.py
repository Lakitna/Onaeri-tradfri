from sys import exc_info
import time

from pytradfri import error
import com
import Onaeri.settings as settings
from Onaeri import data, helper
from Onaeri.logger import log
from lampdata import briRange, colorRange

metrics = {'total': 0, 'color': 0, 'power': 0, 'brightness': 0, 'timeout': 0}


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
                if not cycle.lamp[id].power is None:
                    set(cycle, id)
                    update = True
    if update:
        time.sleep(settings.Global.transitionTime)


def color(api):
    """
    Update the color of one or more lamps in one or more cycles.
    """
    def set(cycle, id):
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

    update = False
    for cycle in api.cycles:
        if cycle.update:
            for id in cycle.lamp:
                if not cycle.lamp[id].color is None:
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
                if not cycle.lamp[id].brightness is None:
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
