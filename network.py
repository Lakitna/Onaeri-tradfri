import os
import uuid
import socket
import subprocess
import re
from Onaeri import helper
from Onaeri.logger import log
from pytradfri.api.libcoap_api import APIFactory
from pytradfri import error

# Clear termnial window
print(chr(27) + "[2J")


class Network:
    def __init__(self):
        log("Connecting to Gateway: ", end="", flush=True)

        self.filePath = "%s/gateway.conf" % (
            os.path.dirname(os.path.abspath(__file__)))
        self._settingVars = ['ip', 'psk', 'identity', 'mac']
        self._separator = "="
        self._settings = self.getSettings()

        if not self._settings['ip'] or not self.ipActive(self._settings['ip']):
            log.warn("No valid IP found in storage.")
            self._settings['ip'] = self.findGatewayIp()
            self.storeSettings(self._settings)

        if not len(self._settings['psk']) == 16:
            log()
            log.warn("No valid Security Code found in storage.")
            log.warn("Gateway guard won't open the door.")
            log.warn("Please enter the Security Code on the back of your " +
                     "Gateway:", end=" ")
            key = input().strip()
            if len(key) < 2:
                log.error("No Security Code provided by user. Exiting.")
                exit()
            else:
                identity = uuid.uuid4().hex
                api_factory = APIFactory(host=self._settings['ip'],
                                         psk_id=identity)

                try:
                    psk = api_factory.generate_psk(key)
                except error.RequestTimeout:
                    log.error("Gateway guard doesn't respond to the " +
                              "Security Code, door remains locked.")
                    log.error("Please check if you made an error while " +
                              "entering the Security Code and try again.")
                    exit()
                log.success("Gateway guard opened the door.")

                self._settings['identity'] = identity
                self._settings['psk'] = psk
                self.storeSettings(self._settings)

        # Make api_factory easily accessible in other modules
        self.api_factory = APIFactory(host=self._settings['ip'],
                                      psk_id=self._settings['identity'],
                                      psk=self._settings['psk'])

    def resetSettings(self):
        """
        Reset/make Gateway settings file
        """
        with open(self.filePath, 'w') as f:
            for var in self._settingVars:
                f.write("%s%s\n" % (var, self._separator))

    def getSettings(self):
        """
        Grab settings from settings file, validate file integrety and output
        as dict
        """
        if not os.path.isfile(self.filePath) \
           or not os.path.getsize(self.filePath) > 0:
                self.resetSettings()

        with open(self.filePath, 'r+') as f:
            ret = {}
            for line in f:
                line = line.strip().split(self._separator)
                key = line[0]
                val = line[1]

                if key not in self._settingVars:
                    log.error("Gateway settings invalid. " +
                              "Unexpected parameter '%s'." % key)
                    exit()
                ret[key] = val

            if not len(ret) == len(self._settingVars):
                params = len(self._settingVars) - len(ret)
                log.error("Gateway settings invalid. " +
                          "Missing %d parameters." % params)
                log.error("Clearing settings and retrying.")
                self.resetSettings()
                return self.getSettings()

        return ret

    def storeSettings(self, values):
        """
        Update settings file. Input is dict
        """
        with open(self.filePath, 'w') as f:
            for key in values:
                if key not in self._settingVars:
                    log.error("Gateway setting invalid. Tried " +
                              "to write unexpected parameter '%s'." % key)
                    exit()

                f.write("%s%s%s\n" % (key, self._separator, values[key]))

    def ipActive(self, ip):
        """
        Check is given IP is active
        """
        proc = subprocess.Popen("fping %s -r 2 2> /dev/null" % ip,
                                stdout=subprocess.PIPE,
                                shell=True)
        (ipState, err) = proc.communicate()
        ipState = str(ipState)

        if 'alive' in ipState:
            return True
        else:
            return False

    def findGatewayIp(self, iteration=False):
        """
        Find IP of gateway using multiple methods
        """
        def updateAPR():
            """
            Update arp table with full network on current subnet
            """
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
            except OSError:
                log()
                log.error("Couldn't find the IP of this machine. " +
                          "Are you connected to the network?")
                exit()

            # Ping entire subnet
            subprocess.call("fping -c 1 -g %s/24 2> /dev/null " % ip +
                            "| grep HackToHideOutput",
                            shell=True)

        def consultARP(regex):
            """
            Look for given regular expression in ARP records and return
            associated IP.
            """
            proc = subprocess.Popen("arp -a | grep -E \"%s\" -i" % regex,
                                    stdout=subprocess.PIPE,
                                    shell=True)
            (arpRecord, err) = proc.communicate()
            arpRecord = str(arpRecord)

            # If there is more than 1 arp record returned
            if len(arpRecord.split("\\n")) > 2:
                return None

            # Find ip4 address in arp record
            regex = re.compile('(([0-9]{1,3}\.){3}[0-9]{1,3})')
            match = regex.search(arpRecord)

            if match is None:
                return None
            return arpRecord[match.start():match.end()]

        log.warn("Looking for Gateway on local network.", end=" ", flush=True)

        if not iteration:
            updateAPR()

        # First attempt at finding gateway by looking for its name
        ip = consultARP("gw\-[a-z0-9]{12}")

        if ip is None:
            if len(self._settings['mac']) < 2:  # If mac address is unkown
                log()
                log.error("Couldn't find gateway by its name.")
                log.error("Please enter the Serial Number on the back of " +
                          "the device:", end=" ")
                mac = input().replace("-", ":")
                if len(mac) < 2:
                    exit()
                self._settings['mac'] = mac
            ip = consultARP(self._settings['mac'])

        if ip is None:
            if not iteration:
                log.error("Couldn't find any gateway by name or Serial " +
                          "Number. Values have been reset, trying again " +
                          "with a blank slate.")
                self._settings['mac'] = ''
                ip = self.findGatewayIp(True)
            else:
                log.error("Couldn't find any gateway by name or Serial " +
                          "Number.")
                log.error("Are you sure the gateway is on?")
                log.error("Are you connected to the correct network?")
                exit()

        if ip is not None:
            if not iteration:
                log.success("IP found", end=" ")
            return ip
