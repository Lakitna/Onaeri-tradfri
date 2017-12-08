from network import Network
import Onaeri.settings as settings
from Onaeri import helper
from Onaeri.logger import log

from pytradfri import Gateway, error

network = Network()

api_factory = network.api_factory
api = api_factory.request

gateway = Gateway()

try:
    devices_command = gateway.get_devices()
    devices_commands = api(devices_command)
    devices = api(devices_commands)
except error.RequestTimeout:
    log.error("Can't connect to Gateway.")
    log.error("Is the Gateway on and connected to the network?")
    log.error("Do you want to reset the Gateway settings? (y/n)")
    inp = input()
    if inp == "y":
        network.resetSettings()
    exit()

# Get list of all controllable lamps
light_objects = [dev for dev in devices if dev.has_light_control]

# Key list of controllable lamps with their lamp name
light_ids = {}
for l in light_objects:
    if l.name in light_ids:
        log.error("Two lamps have the exact same name. " +
                  "Please make all lamp names unique and try again.")
        exit()
    light_ids[l.name] = l

log.success("Done", end="\n\n")
