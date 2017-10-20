from com import lights, api
from pytradfri import error
import sys


class Observer:
    """
    Observe changes in a lamp
    """
    def __init__(self, lampId=0):
        self.update = True
        self._lampId = lampId
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
        for key in new:
            if not prev[key] == new[key] and not (key == 'state' and new[key] == False):
                print("[Observer] Illegal change in lamp %d: %s changed to %s" % (self._lampId, key, new[key]))
                return False
        return True


    def _getData(self):
        """
        Get lamp info from gateway.
        """
        device = lights[self._lampId]

        try:
            api(device.update())
        except error.RequestTimeout:
            sys.stdout.write("\b|")
            sys.stdout.flush()
            return self._prev

        light = device.light_control.lights[0]
        return {'state': light.state, 'bright': light.dimmer, 'color': light.kelvin_color}
