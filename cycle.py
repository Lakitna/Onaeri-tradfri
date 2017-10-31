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
        self.deviation = Deviation( self.cycleSettings )

        self._prevVals = [0,0]


    def tick(self, timeKeeper):
        """
        Progress cycle.
        """
        self.observer.look()

        if timeKeeper.update or self.observer.update:
            newVals = self.lookup.table( timeKeeper.timeCode )

            if self.observer.update:
                self.deviation.change(newVals, self.observer.data)

            # Don't run deviation routine when user turns on the lamp
            if self.observer.turnedOn:
                self.deviation.reset()

            self.deviation.tick()
            # Apply deviation to running cycle
            newVals['brightness'] = helper.limitTo(
                                        newVals['brightness'] + self.deviation.values['brightness'],
                                        settings.Global.briRange
                                    );
            newVals['color'] = helper.limitTo(
                                        newVals['color'] + self.deviation.values['color'],
                                        settings.Global.colorRange
                                    );

            # If the lamp is on and (value is not the same as previous update or observer dictates update)
            if self.observer.data['power'] and (not newVals == self._prevVals or self.observer.update):
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







class Deviation:
    """
    Allow the user to temporary deviate from the given cycle.
    """
    def __init__(self, userSettings):
        self.duration = userSettings.deviationDuration
        self.table = helper.sequenceResize(settings.Global.deviationData, self.duration)

        self.counter = 0
        self.active = False
        self.values = {}
        self.setValues = {}
        self.reset()


    def change(self, dataVals, changeVals):
        """
        Apply an observed change to deviation routine
        """
        self.reset()

        if changeVals['power'] and self.duration > 0:
            self.setValues['brightness'] = changeVals['brightness'] - dataVals['brightness']
            self.setValues['color'] = changeVals['color'] - dataVals['color']

            if not helper.inRange(self.setValues['brightness'], (-1,1)) \
               or not helper.inRange(self.setValues['color'], (-10,10)):
                self.active = True


    def tick(self):
        """
        Progress by one tick
        """
        if self.active:
            if self.counter >= self.duration:
                self.reset()

            multiplier = self.table[self.counter] / 100

            self.values['brightness'] = round(self.setValues['brightness'] * multiplier)
            self.values['color'] = round(self.setValues['color'] * multiplier)

            self.counter += 1


    def reset(self):
        """
        Reset the deviation routine
        """
        self.counter = 0
        self.active = False
        self.values = {'brightness': 0, 'color': 0}
        self.setValues = self.values
