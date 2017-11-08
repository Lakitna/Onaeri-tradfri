from os import path
import socket
import subprocess
import re
import Onaeri.settings as settings
from Onaeri import helper

print("Getting network data from gateway: ", end="", flush=True)

from pytradfri import Gateway, error
from pytradfri.api.libcoap_api import APIFactory




def activeIp(ip):
    proc = subprocess.Popen("fping %s -r 2 2> /dev/null" % ip, stdout=subprocess.PIPE, shell=True)
    (ipState, err) = proc.communicate()
    ipState = str(ipState)

    if 'alive' in ipState:
        return True
    else:
        return False


def findGatewayIp():
    helper.printWarning("Attempting to find Gateway on local network.", end=" ", flush=True)

    def hostIp():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except OSError:
            print()
            helper.printError("Couldn't find the IP of this machine. Are you connected to the network?")
            exit()
    ip = hostIp()


    keyword = 'tradfri-gateway'

    # Update arp table with full network on current subnet
    subprocess.call("fping -c 1 -g %s/24 2> /dev/null | grep %s" % (ip, keyword), shell=True)

    # Read arp table and look for keyword
    proc = subprocess.Popen("arp -a | grep %s --ignore-case" % keyword, stdout=subprocess.PIPE, shell=True)
    (arpRecord, err) = proc.communicate()
    arpRecord = str(arpRecord)

    # Find ip4 address in arp record
    regex = re.compile('([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})')
    match = regex.search(arpRecord)
    if match is None:
        return None

    return arpRecord[match.start():match.end()]




filePath = path.dirname(path.abspath(__file__))

with open('%s/gateway_ip.txt' % filePath, 'a') as file:
    pass
with open('%s/gateway_ip.txt' % filePath, 'r+') as file:
    file.seek(0)
    ip = file.read().strip()
    if not ip or not activeIp(ip):
        helper.printWarning("No valid IP found.", end=" ", flush=True)
        ip = findGatewayIp()
        file.seek(0)
        file.write(ip)

    api_factory = APIFactory(ip)

with open('%s/gateway_psk.txt' % filePath, 'a+') as file:
    file.seek(0)
    psk = file.read().strip()
    if psk:
        # Use stored key
        api_factory.psk = psk
    else:
        # Generate new key
        helper.printWarning("\nEnter key on the back of your Gateway:", end=" ")
        key = input()
        if len(key) < 16:
            helper.printError("Key is too short. It should be 16 characters")
            exit()
        elif len(key) > 16:
            helper.printError("Key is too long. It should be 16 characters")
            exit()
        else:
            psk = api_factory.generate_psk(key)
            print('Generated PSK: ', psk)
            file.write(psk)



api = api_factory.request

gateway = Gateway()


devices_command = gateway.get_devices()
devices_commands = api(devices_command)
devices = api(devices_commands)


# Get list of all controllable lamps
light_objects = [dev for dev in devices if dev.has_light_control]

helper.printDone()
