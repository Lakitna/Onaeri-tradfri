import settings
import com
import control
from timecode import TimeCode
from lookup import Lookup
from observer import Observer


class Cycle:
    'Cycle a group of lamps'
    def __init__(self, group, *, wakeTime=settings.userAlarmTime, sleepTime=settings.userSleepTime):
        self.group = group
        # Lookup class setup
        self.data = Lookup( wakeTime, sleepTime )
        # Observer class setup for first lamp in group
        self.obs = Observer( self.group[0] )
        # Make list to keep track of value changes
        self.prevVals = [999,999]


    def tick(self, tc):
        'Progress cycle'
        # Observe changes
        self.obs.do()

        # If new timecode or observer dictates update
        if tc.update or self.obs.update:
            # Get new data from Lookup class
            vals = self.data.get( tc.get() )

            # If the vals have changed or observer dictates update
            if not vals == self.prevVals or self.obs.update:
                # Set lamp values
                self._setVals(vals, tc)
                # Prevent observer from overturning legal changes.
                self.obs.notifyLegalChange()


            # Only set lamp state on timecode update flag to enable manually
            # turning the lamps back on after auto-change.
            if tc.update:
                if self.data.setState( tc.get(), self.group ):
                    # Prevent observer from overturning legal changes.
                    self.obs.notifyLegalChange()


            # Prep for next loop
            self.prevVals = vals




    def _setVals(self, v, tc):
        'Set lamp values'
        print("[%s] Setting lamp %s to {bri: %d, color: %d}" % (tc.decode(), self.group, v[0], v[1]))
        # Change color
        control.color( settings.colorValues[ v[1] ], self.group )
        # Change brightness
        control.brightness( v[0], self.group )
