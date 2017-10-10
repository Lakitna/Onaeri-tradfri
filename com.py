import sys
import settings

from pytradfri import Gateway, error
from pytradfri.api.libcoap_api import api_factory


print("Getting network data from gateway:")

# Setup communication with the gateway
try:
    api = api_factory(settings.gatewayIp, settings.gatewayKey)
except error.RequestTimeout:
    print("Couldn't reach gateway. Please check the settings in settings.py and try again.")
    print("Exiting Onaeri")
    exit()


gateway = Gateway()
print("#", end="")


# Get lamp network state and devices. Prep them for use
devices_command = gateway.get_devices()
print("#", end="")
devices_commands = api(devices_command)
print("#", end="")
devices = api(*devices_commands)
print(" Done")
print()


# Get list of all controllable lamps
lights = [dev for dev in devices if dev.has_light_control]
