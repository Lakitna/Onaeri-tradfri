import threading
import time
import com


class Observer:
    'Observe changes in light status'
    def __init__(self, device_id=0):
        self._active = False
        self._prevState = False
        self.update = True
        self._device_id = device_id


    def start(self):
        'Start observer if it is not active'
        if self._active == False:
            self._observe()

    def _observe(self):
        self._active = True

        device = com.lights[self._device_id]

        def callback(updated_device):
            # Callback if observer noticed a change in the lamps parameters
            light = updated_device.light_control.lights[self._device_id]
            newState = light.state

            # If the lamp state changed set update flag
            if not self._prevState == newState and newState == True:
                self.update = True
            else:
                self.update = False

            # Print new parameters to the console
            print("[Observer] <#%d\t| On: %s\t| Bri: %d\t| Color: %s | Update: %s>" % (light.index, light.state, light.dimmer, light.xy_color, self.update))

            # Prep for next instance
            prevState = newState

        def err_callback(err):
            # Catch errors
            print("[Observer] %s" % err)
            self._active = False

        def worker():
            com.api(device.observe(callback, err_callback, duration=1000))

        threading.Thread(target=worker, daemon=True).start()
        print("[Observer] Observing started.")
        time.sleep(1)
