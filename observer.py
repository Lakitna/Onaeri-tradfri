from com import lights, api
from pytradfri import error
import sys


class Observer:
    """
    Observe changes in a lamp
    """
    def __init__(self, lampIds=[0]):
        self.update = True
        self._lampIds = lampIds
        self.data = {'brightness': 0, 'color': 0, 'power': False}
        self._legalChange = True
        self.turnedOn = False


    def look(self):
        """
        Look for changes in lamp values
        """
        self.turnedOn = False
        self.update = False

        newData = self._getData()


        for i in range(len(newData)):
            if self.data['power'] == False and newData[i]['power'] == True:
                self.turnedOn = True


        if not self._legalChange:
            self.data = self._sameData(newData, self.data)
        else:
            self.data = newData[0]


        self._legalChange = False


    def legalChange(self):
        """
        Prevent observer from overwriting next detected change.
        """
        self._legalChange = True


    def _sameData(self, new, prev):
        """
        Compare new to previous observed values. Returns True when both sets are the same.
        """
        for i in range(len(new)):
            lamp = new[i]
            for key in lamp:
                if not prev[key] == new[i][key]:
                    print()
                    print("[Observer] Illegal change in lamp %d: %s changed to %s" % (self._lampIds[i], key, new[i][key]))
                    self.update = True
                    return lamp
        return new[0]


    def _getData(self):
        """
        Get lamp info from gateway.
        """
        ret = []
        for lampId in self._lampIds:
            device = lights[lampId]

            try:
                api(device.update())
            except error.RequestTimeout:
                sys.stdout.write("\b|")
                sys.stdout.flush()
                return [self.data]

            light = device.light_control.lights[0]

            power = False
            if device.reachable:  power = light.state

            ret.append( {'brightness': light.dimmer, 'color': light.kelvin_color_inferred, 'power': power} )
        return ret
