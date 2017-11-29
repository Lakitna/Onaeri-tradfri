from sys import exc_info
import time

from pytradfri import error
import com
import Onaeri.settings as settings
from Onaeri import data, helper
from Onaeri.logger import *
from lampdata import briRange, colorRange

metrics = {'total': 0, 'color': 0, 'power': 0, 'brightness': 0, 'timeout': 0}

def power(api):
    """
    Turn one or more lamps in one or more cycles on or off.
    """
    for cycle in api.cycles:
        if cycle.update and not cycle.lamp.power == None:
            for l in _selectLights(cycle, stateChange=True):
                command = l.light_control.set_state(cycle.lamp.power)
                _sendCommand(command)
                metrics['power'] += 1

        if cycle.lamp.mode == "dark":
            lamps = _selectLights(cycle)
            if len(lamps) > 1:
                for i in range(len(lamps)):
                    if i % 2:
                        command = lamps[i].light_control.set_state(False)
                        _sendCommand(command)
                        metrics['power'] += 1


def color(api):
    """
    Update the color of one or more lamps in one or more cycles.
    """
    for cycle in api.cycles:
        if cycle.update and not cycle.lamp.color == None:
            val = helper.scale(cycle.lamp.color, settings.Global.valRange, colorRange)

            for l in _selectLights(cycle):
                command = l.light_control.set_color_temp(val, transition_time=settings.Global.transitionTime*10)
                _sendCommand(command)
                metrics['color'] += 1


def brightness(api):
    """
    Update the brightness of one or more lamps in one or more cycles.
    """
    for cycle in api.cycles:
        if cycle.update and not cycle.lamp.brightness == None:
            val = helper.scale(cycle.lamp.brightness, settings.Global.valRange, briRange)
            lamps = _selectLights(cycle)

            if cycle.lamp.mode == "dark":
                if len(lamps) > 1:
                    for i in range(len(lamps)):
                        if not i % 2:
                            command = lamps[i].light_control.set_dimmer(val, transition_time=settings.Global.transitionTime*10)
                            _sendCommand(command)
                            metrics['brightness'] += 1
            else:
                for l in lamps:
                    command = l.light_control.set_dimmer(val, transition_time=settings.Global.transitionTime*10)
                    _sendCommand(command)
                    metrics['brightness'] += 1




def _sendCommand(command, iteration=1):
    """
    Send command with retry on timeout
    """
    try:
        com.api(command)
        metrics['total'] += 1
        time.sleep(settings.Global.transitionTime / 2)
    except error.RequestTimeout:
        logWarn("[Control] Timeout error on try %d" % iteration)
        metrics['timeout'] += 1
        if iteration < settings.Global.commandsTries:
            _sendCommand(command, iteration=iteration+1)


def _selectLights(cycle, *, stateChange=False):
    """
    Select lamps
    """
    try:
        return com.light_groups[cycle.name]
    except KeyError:
        logError("No lamps available for cycle `%s`." % cycle.name)
