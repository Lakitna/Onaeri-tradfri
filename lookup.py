from timekeeper import TimeKeeper
import control
import time
import settings
import helper


class Lookup:
    """
    Calculates and dispenses lookup tables for light values
    """
    def __init__(self, config):
        cycleName = config.__name__.split(".")[1]
        print("Building lookup table for %s: " % cycleName, end="", flush=True)

        timeKeeper = TimeKeeper();
        self.config = config

        # Sleep rhythm settings
        self._userAlarmTime =    timeKeeper.makeCode(self.config.userAlarmTime)
        self._userAlarmOffset =  timeKeeper.makeCode(m=self.config.userAlarmOffset)

        self._userSleepTime =    timeKeeper.makeCode(self.config.userSleepTime)
        self._userWindDownTime = timeKeeper.makeCode(m=self.config.userWindDownTime)


        # Create morning and evening slopes based on sleep rhythm settings
        self._userMorningSlope = [0,0]
        self._userMorningSlope[0] = self._userAlarmTime - self._userAlarmOffset
        self._userMorningSlope[1] = self._userMorningSlope[0] + self.config.morningSlopeDuration

        self._userEveningSlope = [0,0,0,0]
        self._userEveningSlope[0] = self._userSleepTime - self.config.eveningSlopeDuration
        self._userEveningSlope[1] = self._userSleepTime
        self._userEveningSlope[2] = self._userEveningSlope[0]
        if self._userEveningSlope[0] < 0:
            self._userEveningSlope[0] = 0
            self._userEveningSlope[2] += self.config.totalDataPoints
            self._userEveningSlope[3] = self.config.totalDataPoints


        # Build lookup tables
        self.brightness = self._buildTable(settings.Global.brightnessData, self.config.briCorrect)
        self.color = self._buildTable(settings.Global.colorData, self.config.colorCorrect)

        helper.printDone()
        # print(self.brightness)
        # print()
        # print(self.color)
        # exit()


    def table(self, timeCode):
        """
        Get the values associated with timecode
        """
        brightness = helper.scale(self.brightness[timeCode], (0,100), settings.Global.briRange, decimals=0)
        color      = helper.scale(self.color[timeCode], (0,100), settings.Global.colorRange, decimals=0)


        if timeCode == (self._userAlarmTime - self._userAlarmOffset):
            power = True
        elif timeCode == self._userSleepTime:
            power = False
        else:
            power = None

        return {"brightness": brightness, "color": color, "power": power}



    def _buildTable(self, source, sourceRange):
        """
        Build a lookup table based on class attributes and a given data source.
        """
        # Resize morningSlope and eveningSlope
        source['morning'] = helper.sequenceResize(source['morning'], self.config.morningSlopeDuration)
        source['evening'] = helper.sequenceResize(source['evening'], self.config.eveningSlopeDuration)


        # Create full table and default to nightflat
        table = [source['night']+sourceRange[0]] * settings.Global.totalDataPoints

        for timeCode in range(self._userMorningSlope[0], self._userMorningSlope[1]):
            table[timeCode] = source['morning'][timeCode - self._userMorningSlope[0]]
            table[timeCode] = helper.scale(table[timeCode], (0,100), sourceRange)
            # print("morning %s > %s" % (timeCode, table[timeCode]))


        for timeCode in range(self._userEveningSlope[0], self._userEveningSlope[1]):
            table[timeCode] = source['evening'][timeCode - self._userEveningSlope[0]]
            table[timeCode] = helper.scale(table[timeCode], (0,100), sourceRange)
            # print("evening %s > %s" % (timeCode, table[timeCode]))

        for timeCode in range(self._userEveningSlope[2], self._userEveningSlope[3]):
            table[timeCode] = source['evening'][timeCode - self._userEveningSlope[2]]
            table[timeCode] = helper.scale(table[timeCode], (0,100), sourceRange)
            # print("evening %s > %s" % (timeCode, table[timeCode]))


        for timeCode in range(self._userMorningSlope[1], self._userEveningSlope[2]):
            table[timeCode] = helper.scale(source['day'], (0,100), sourceRange)
            # print("day %s > %s" % (timeCode, table[timeCode]))


        return table
