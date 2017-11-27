from network import Network
import Onaeri.settings as settings
from Onaeri import helper
from Onaeri.logger import *

from pytradfri import Gateway, error
from pytradfri.api.libcoap_api import APIFactory

network = Network()

api_factory = network.api_factory
api = api_factory.request

gateway = Gateway()

try:
    devices_command = gateway.get_devices()
    devices_commands = api(devices_command)
    devices = api(devices_commands)
except error.RequestTimeout:
    logError("Can't connect to Gateway.")
    logError("Is the Gateway on and connected to the network?")
    logError("Do you want to reset the Gateway settings? (y/n)")
    inp = input()
    if inp == "y":
        network.resetSettings()
        helper.programRestart()
    exit()

# Get list of all controllable lamps
light_objects = [dev for dev in devices if dev.has_light_control]

logSuccess("Done", end="\n\n")
