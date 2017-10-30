import settings
import helper

print("Getting network data from gateway: ", end="", flush=True)

from pytradfri import Gateway, error
from pytradfri.api.libcoap_api import api_factory


# Setup communication with the gateway
try:
    api = api_factory(settings.Global.gatewayIp, settings.Global.gatewayKey)
except error.RequestTimeout:
    helper.printError("Couldn't reach gateway. Please check the settings in settings.py and try again.")
    helper.printError("Exiting Onaeri")
    exit()


gateway = Gateway()


# Get lamp network state and devices. Prep them for use
devices_command = gateway.get_devices()
devices_commands = api(devices_command)
devices = api(devices_commands)

helper.printDone()


# Get list of all controllable lamps
lights = [dev for dev in devices if dev.has_light_control]
