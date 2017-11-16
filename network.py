from os import path
import socket
import subprocess
import re
from Onaeri import helper
from Onaeri.logger import *
from pytradfri.api.libcoap_api import APIFactory


class Network:
    def __init__(self):
        log("Validating Gateway connection information: ", end="", flush=True)
        self.filePath = "%s/gateway_settings.txt" % path.dirname(path.abspath(__file__))
        self._comVars = ['ip', 'psk', 'mac']
        self._separator = "="
        self._settings = self.getSettings()

        self.ip = None
        self.psk = None


        if not self._settings['ip'] or not self.ipActive( self._settings['ip'] ):
            logWarn("No valid IP found.", end=" ", flush=True)
            self._settings['ip'] = self.findGatewayIp()
            self.updateSettings( self._settings )

        if not len(self._settings['psk']) == 16:
            # Generate new key
            log()
            logWarn("No valid Security Code found.")
            logWarn("Please enter the Security Code on the back of your Gateway:", end=" ")
            key = input().strip()
            if len(key) < 2:
                logError("No Security Code provided by user. Exiting.")
                exit()
            else:
                api_factory = APIFactory(self._settings['ip'])
                self._settings['psk'] = api_factory.generate_psk(key)
                log('Generated PSK: ', self._settings['psk'])
                self.updateSettings(self._settings)


        # Make easily available after import
        self.psk = self._settings['psk']
        self.ip = self._settings['ip']

        logSuccess("Done")



    def resetSettings(self):
        """
        Reset/make Gateway settings file
        """
        with open(self.filePath, 'w') as f:
            for var in self._comVars:
                f.write("%s%s\n" % (var, self._separator))

    def getSettings(self):
        """
        Grab settings from settings file, validate file integrety and output as dict
        """
        if not path.isfile(self.filePath) or not path.getsize(self.filePath) > 0:
            self.resetSettings()

        with open(self.filePath, 'r+') as f:
            ret = {}
            for line in f:
                line = line.strip().split(self._separator)
                key = line[0]
                val = line[1]

                if not key in self._comVars:
                    logError("Gateway settings invalid. Unexpected parameter '%s'." % key)
                    exit()

                ret[key] = val
        return ret


    def updateSettings(self, values):
        """
        Update settings file. Input is dict
        """
        with open(self.filePath, 'w') as f:
            for key in values:
                if not key in self._comVars:
                    logError("Gateway setting invalid. Tried to write unexpected parameter '%s'." % key)
                    exit()

                f.write("%s%s%s\n" % (key, self._separator, values[key]))



    def ipActive(self, ip):
        """
        Check is given IP is active
        """
        proc = subprocess.Popen("fping %s -r 2 2> /dev/null" % ip, stdout=subprocess.PIPE, shell=True)
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
                logError("Couldn't find the IP of this machine. Are you connected to the network?")
                exit()

            # Ping entire subnet
            subprocess.call("fping -c 1 -g %s/24 2> /dev/null | grep HackToHideOutput" % ip, shell=True)


        def consultARP(keyword):
            """
            Look for given keyword in ARP records and return associated IP.
            """
            proc = subprocess.Popen("arp -a | grep %s --ignore-case" % keyword, stdout=subprocess.PIPE, shell=True)
            (arpRecord, err) = proc.communicate()
            arpRecord = str(arpRecord)

            # Find ip4 address in arp record
            regex = re.compile('([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})')
            match = regex.search(arpRecord)

            if match is None:
                return None
            return arpRecord[match.start():match.end()]


        logWarn("Looking for Gateway on local network.", end=" ", flush=True)

        if not iteration:
            updateAPR()

        # First attempt at finding gateway by looking for its name
        ip = consultARP('tradfri')

        if ip is None:
            if len(self._settings['mac']) < 2: # If mac address is unkown
                log()
                logError("Couldn't find gateway by its name.")
                logError("Please enter the Serial Number on the back of the device:", end=" ")
                mac = input().replace("-", ":")
                if len(mac) < 2:
                    exit()
                self._settings['mac'] = mac
            ip = consultARP(self._settings['mac'])

        if ip is None:
            if not iteration:
                logError("Couldn't find any gateway by name or Serial Number. Values have been reset, trying again with a blank slate.")
                self._settings['mac'] = ''
                ip = self.findGatewayIp(True)
            else:
                logError("Couldn't find any gateway by name or Serial Number.")
                logError("Are you sure the gateway is on?")
                logError("Are you connected to the correct network?")
                exit()

        if not ip is None:
            if not iteration:
                logSuccess("IP found", end=" ")
            return ip
