import com
from pytradfri import error


class Observer:
    'Observe changes in lamp'
    def __init__(self, device_id=0):
        self.update = True
        self._device_id = device_id
        self._prev = self._get_data()
        self._legalChange = False


    def do(self):
        'Check for changes in lamp values'
        # Get data from gateway
        new = self._get_data()

        # Unset update flag
        self.update = False

        # Check if the lamp illegally updated, set update flag if it did
        if not self._legalChange:
            # If no legal change was reported:
            for key in new:
                # For all lamp values do:
                if not self._prev[key] == new[key]:
                    # If value has changed:
                    if not (key == 'state' and not new[key]):
                        # If lamp was not just turned off:
                        self.update = True
                        print("[Observer] Illegal change in %d: %s changed to %s" % (self._device_id, key, new[key]))
                        break

        # Prep for next iteration
        self._prev = new
        self._legalChange = False


    def notifyLegalChange(self):
        'Prevent observer from overwriting legal changes'
        # print("[Observer] Legal change incomming, ignoring next")
        self._legalChange = True


    def _get_data(self):
        'Get lamp info from gateway'
        # Select active device
        device = com.lights[self._device_id]

        try:
            # Get active device data from gateway
            com.api(device.update())
        except error.RequestTimeout:
            print("[Observer] Timeout error: retrieving data from Gateway failed")
            return self._prev

        # Select lamp
        light = device.light_control.lights[0]
        # Gather relevant lamp info and return
        return {'state': light.state, 'bright': light.dimmer, 'color': light.kelvin_color}
