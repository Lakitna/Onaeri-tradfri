from sys import exc_info
import time

from pytradfri import error
import com
import settings
import helper


def state(val, lightIndex=None):
    """
    Turn one or more lamps on or off.
    """
    if val is None:  return
    if val is True or val is False:
        print("[Control] State change %s to %s" % (lightIndex, val))
        for l in _selectLights(lightIndex, stateChange=True):
            command = l.light_control.set_state(val)
            _sendCommand(command)
        return

    else:
        print("[Control] Input value error. Allowed values 'True', 'False' or 'None'.")
        return


def color(val, lightIndex=None):
    """
    Update the color of one or more lamps.
    """
    if helper.inRange(val, settings.app.colorRange):
        for l in _selectLights(lightIndex):
            command = l.light_control.set_kelvin_color(val)
            _sendCommand(command)
        return
    else:
        print("[Control] Color input value error. Allowed range %s, %d given." % (settings.app.colorRange, val))
        return


def brightness(val, lightIndex=None):
    """
    Update the brightness of one or more lamps.
    """
    if helper.inRange(val, settings.app.briRange):
        for l in _selectLights(lightIndex):
            command = l.light_control.set_dimmer(val, transition_time=settings.app.transitionTime*10)
            _sendCommand(command)
        return
    else:
        print("[Control] Brightness input value error. Allowed range %s, %d given." % (settings.app.briRange, val))
        return




def _sendCommand(command, iteration=1):
    """
    Send command with retry on timeout
    """
    try:
        com.api(command)
    except error.RequestTimeout:
        print("[Control] Timeout error on try", iteration)
        if iteration < settings.app.commandsTries:
            _sendCommand(command, iteration=iteration+1)


def _selectLights(lightIndex, *, stateChange=False):
    """
    Select lamps
    """
    if lightIndex == None:
        lightIndex = []
        for i in range(len(com.lights)):
            lightIndex.append(i)


    ret = []
    for i in lightIndex:
        try:
            if com.lights[i].light_control.lights[0].state or stateChange:
                ret.append(com.lights[i])
        except IndexError:
            print("[Control] Selected lamp #%d is unkown" % i)
    return ret
