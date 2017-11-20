from sys import exc_info
import time

from pytradfri import error
import com
import Onaeri.settings as settings
from Onaeri import data, helper
from Onaeri.logger import *
from lampdata import briRange, colorRange

count = {'total': 0, 'color': 0, 'power': 0, 'brightness': 0, 'timeouts': 0}

def power(api):
    """
    Turn one or more lamps in one or more cycles on or off.
    """
    for cycle in api.cycles:
        if cycle.update and not cycle.lamp.power == None:

            for l in _selectLights(cycle.group, stateChange=True):
                command = l.light_control.set_state(cycle.lamp.power)
                _sendCommand(command)
                count['power'] += 1
            continue


def color(api):
    """
    Update the color of one or more lamps in one or more cycles.
    """
    for cycle in api.cycles:
        if cycle.update and not cycle.lamp.color == None:

            for l in _selectLights(cycle.group):
                val = helper.scale(cycle.lamp.color, settings.Global.valRange, colorRange)
                command = l.light_control.set_color_temp(val)
                _sendCommand(command)
                count['color'] += 1
            continue


def brightness(api):
    """
    Update the brightness of one or more lamps in one or more cycles.
    """
    for cycle in api.cycles:
        if cycle.update and not cycle.lamp.brightness == None:

            for l in _selectLights(cycle.group):
                val = helper.scale(cycle.lamp.brightness, settings.Global.valRange, briRange)
                command = l.light_control.set_dimmer(val, transition_time=settings.Global.transitionTime*10)
                _sendCommand(command)
                count['brightness'] += 1
            continue




def _sendCommand(command, iteration=1):
    """
    Send command with retry on timeout
    """
    try:
        com.api(command)
        count['total'] += 1
    except error.RequestTimeout:
        logWarn("[Control] Timeout error on try %d" % iteration)
        count['timeout'] += 1
        if iteration < settings.Global.commandsTries:
            _sendCommand(command, iteration=iteration+1)


def _selectLights(lightIndex, *, stateChange=False):
    """
    Select lamps
    """
    if lightIndex == None:
        lightIndex = []
        for i in range(len(com.light_objects)):
            lightIndex.append(i)
    if type(lightIndex) is int:
        lightIndex = [lightIndex]


    ret = []
    for i in lightIndex:
        try:
            if com.light_objects[i].light_control.lights[0].state or stateChange:
                ret.append(com.light_objects[i])
        except IndexError:
            log
            Error("[Control] Selected lamp #%d is unkown" % i)
    return ret
