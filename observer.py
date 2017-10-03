import com
from pytradfri import error


class Observer:
    'Observe changes in light status'
    def __init__(self, device_id=0):
        self.update = True
        self._device_id = device_id
        self._prev = self._get_data()


    def do(self):
        'Get lamp info from gateway and check for changes'
        # Get data from gateway
        new = self._get_data()

        # Unset update flag
        self.update = False
        # Check if the lamp updated, set update flag if it did
        for key in new:
            if not self._prev[key] == new[key]:
                self.update = True
                print("[Observer] %s changed to %s" % (key, new[key]))

        # Prep for next iteration
        self._prev = new


    def _get_data(self):
        'Get lamp info from gateway'
        # Select active device
        device = com.lights[self._device_id]

        try:
            # Get active device data from gateway
            com.api(device.update())
        except error.RequestTimeout:
            print("Timeout error")
            return self._prev

        # Select lamp
        light = device.light_control.lights[self._device_id]
        # Gather relevant lamp info and return
        return {'state': light.state, 'bright': light.dimmer, 'color': light.kelvin_color}
