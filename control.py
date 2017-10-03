import sys
import time

import com
from pytradfri import error


defaultTransitionTime = .5  # In seconds
sendCommandsTries = 3       # In number of tries per command


def state(val, lightIndex=None):
    # Turn one or more lamps on or off
    if val == True or val == False:
        print("[Control] State change to", val)
        for l in _selectLights(lightIndex, state=True):
            command = l.light_control.set_state(val)
            _sendCommand(command)
    else:
        print("[Control] state input value error")
        return False



def color(val, lightIndex=None):
    # Update the color of one or more lamps
    if val < 2200 or val > 4000:
        print("[Control] color input value error")
        return False
    else:
        for l in _selectLights(lightIndex):
            command = l.light_control.set_kelvin_color(val)
            _sendCommand(command)



def brightness(val, lightIndex=None):
    # Update the brightness of one or more lamps
    if val < 0 or val > 255:
        print("[Control] brightness input value error")
        return False
    else:
        for l in _selectLights(lightIndex):
            command = l.light_control.set_dimmer(val, transition_time=defaultTransitionTime*10)
            _sendCommand(command)

        # Wait for the duration of the transition
        time.sleep( defaultTransitionTime * 1.1 )






def _sendCommand(command, *, iteration=1):
    # Send command with error catching and retry on timeout
    try:
        com.api(command)
    except error.RequestTimeout:
        # Catch timeout errors and retry
        print("[ERROR] Timeout on try ", iteration)
        if iteration < sendCommandsTries:
            _sendCommand(command, iteration=iteration+1)
        pass
    except KeyboardInterrupt:
        # Add opportunity to exit during superspeed mode
        print("KeyboardInterrupt")
        exit()
    except:
        # Unexpected errors
        print("[ERROR] ", sys.exc_info()[0])
        print()


def _selectLights(lightIndex, *, state=False):
    # Select all light objects
    if lightIndex == None:
        # Use all connected lights
        ret = []
        for i in range(len(com.lights)):
            # Ignore lights that are off with exception for changing lamp state
            if com.lights[i].light_control.lights[i].state or state:
                ret.append(com.lights[i])
        return ret
    else:
        # Use all specified lights
        ret = []
        for i in lightIndex:
            try:
                # Ignore lights that are off with exception for changing lamp state
                if com.lights[i].light_control.lights[i].state or state:
                    ret.append(com.lights[i])
            except IndexError:
                print("[Control] Selected lamp #%d is unkown" % i)
                pass
        return ret
