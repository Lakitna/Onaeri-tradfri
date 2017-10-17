import settings
import control
from lookup import Lookup
from observer import Observer


class Cycle:
    """
    Cycle a group of lamps
    """
    def __init__(self, group, settingFile=None):
        if not settingFile is None:
            self.cycleSettings = settings.get(settingFile)

        self.group = group
        self.lookup = Lookup( self.cycleSettings )
        self.observer = Observer( self.group[0] ) # Always observe first lamp in group

        self._prevVals = [0,0]
        print()


    def tick(self, timeKeeper):
        """
        Progress cycle.
        """
        self.observer.look()

        if timeKeeper.update or self.observer.update:
            newVals = self.lookup.table( timeKeeper.timeCode )

            # If the vals have changed or observer dictates update
            if (not newVals == self._prevVals) or self.observer.update:
                self._update(newVals)
                print("[%s] Setting lamp %s to {bri: %d, color: %d}" % (timeKeeper.timeStamp(), self.group, newVals['brightness'], newVals['color']))

            # Prep for next loop
            self._prevVals = newVals


    def _update(self, vals):
        """
        Updates lamps in cycle group to new values.
        """
        control.color( settings.Global.colorValues[ vals['color'] ], self.group )
        control.brightness( vals['brightness'], self.group )

        # Don't allow the observer to overwrite turning on a lamp
        if not self.observer.update and vals['power'] is not None:
            control.state( vals['power'], self.group )

        # Prevent observer from overturning legal changes.
        self.observer.legalChange()
