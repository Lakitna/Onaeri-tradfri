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
        self._prev = self._getData()
        self._legalChange = False


    def look(self):
        """
        Look for changes in lamp values
        """
        newData = self._getData()

        self.update = False

        if not self._legalChange:
            if not self._sameData(newData, self._prev):
                self.update = True

        # Prep for next iteration
        self._prev = newData
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
                if not prev[i][key] == new[i][key] and not (key == 'state' and new[i][key] == False):
                    print()
                    print("[Observer] Illegal change in lamp %d: %s changed to %s" % (self._lampIds[i], key, new[i][key]))
                    return False
        return True


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
                return self._prev

            light = device.light_control.lights[0]
            ret.append( {'state': light.state, 'bright': light.dimmer, 'color': light.kelvin_color_inferred} )
        return ret
