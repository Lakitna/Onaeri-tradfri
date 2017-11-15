from network import Network
import Onaeri.settings as settings
from Onaeri import helper

from pytradfri import Gateway, error
from pytradfri.api.libcoap_api import APIFactory

network = Network()

print("Getting network data from Gateway: ", end="", flush=True)


api_factory = APIFactory(network.ip)
api_factory.psk = network.psk

api = api_factory.request

gateway = Gateway()

try:
    devices_command = gateway.get_devices()
    devices_commands = api(devices_command)
    devices = api(devices_commands)
except error.RequestTimeout:
    helper.printError("Can't connect to Gateway.")
    helper.printError("Is the Gateway on and connected to the network?")
    helper.printError("Do you want to reset the Gateway settings? (y/n)")
    inp = input()
    if inp == "y":
        gateway_settings.resetSettings()
    exit()


# Get list of all controllable lamps
light_objects = [dev for dev in devices if dev.has_light_control]

helper.printDone()
