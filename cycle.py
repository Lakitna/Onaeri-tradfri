import settings
import control
from lookup import Lookup
from observer import Observer
import com
import helper


class Cycle:
    """
    Cycle a group of lamps
    """
    def __init__(self, name):
        print()
        self.name = name
        self.cycleSettings = settings.get( self.name )
        self.group = self._lampNameToIds( self.name )
        self.lookup = Lookup( self.cycleSettings )
        self.observer = Observer( self.group[0] ) # Always observe first lamp in group

        self._prevVals = [0,0]


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
                print("[%s] Setting cycle %s %s to {bri: %d, color: %d}" % (timeKeeper.timeStamp(), self.name, self.group, newVals['brightness'], newVals['color']))

            # Prep for next loop
            self._prevVals = newVals


    def _update(self, vals):
        """
        Updates lamps in cycle group to new values.
        """
        control.color( vals['color'], self.group )
        control.brightness( vals['brightness'], self.group )

        # Don't allow the observer to overwrite turning on a lamp
        if not self.observer.update and vals['power'] is not None:
            if self.cycleSettings.automaticStateChange:
                control.state( vals['power'], self.group )

        # Prevent observer from overturning legal changes.
        self.observer.legalChange()


    def _lampNameToIds(self, name):
        """
        Get lamp ids (plural) based on a partial device name.
        """
        ret = []
        for i in range(len(com.lights)):
            if name.lower() in com.lights[i].name.lower():
                ret.append(i)

        if len(ret) == 0:
            ret = [0] # Default to lamp 0
            helper.printError("[Cycle] No lamps found with partial name `%s`. Use the Ikea Tradfri app to change the name of a lamp." % name)
        return ret
