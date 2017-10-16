from timekeeper import TimeKeeper
import control
import time
import settings


class Lookup:
    """
    Calculates and dispenses lookup tables for light values
    """
    def __init__(self, config):
        print("Building lookup table: ", end="", flush=True)
        timeKeeper = TimeKeeper();
        self.config = config

        # Calculate the limits of brightness and color
        self.briLimit =   self._limitRange(settings.Global.briRange, self.config.briCorrect)
        self.colorLimit = self._limitRange(settings.Global.colorRange, self.config.colorCorrect)


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
        self.brightness = self._buildTable(settings.Global.brightnessData)
        self.color = self._buildTable(settings.Global.colorData)

        print("Done")
        # print(self.brightness)
        # print()
        # print(self.color)



    def table(self, timeCode):
        """
        Get the values associated with timecode
        """
        brightness = round(
                (self.brightness[timeCode] / 100)
                * (self.briLimit[1] - self.briLimit[0])
                + self.briLimit[0]
            )
        color = round(
                (self.color[timeCode] / 100)
                * (self.colorLimit[1] - self.colorLimit[0])
                + self.colorLimit[0]
            )

        if timeCode == (self._userAlarmTime - self._userAlarmOffset):
            power = True
        elif timeCode == self._userSleepTime:
            power = False
        else:
            power = None

        return {"brightness": brightness, "color": color, "power": power}



    def _limitRange(self, absoluteRange, correction):
        """
        Limit an absolute range based on a percentage correction tuple
        """
        rangeDifference = absoluteRange[1] - absoluteRange[0]
        out = [0,0]
        out[0] = round(
                (correction[0] / 100)
                * rangeDifference
                + absoluteRange[0]
            )
        out[1] = round(
                (correction[1] / 100)
                * rangeDifference
                + absoluteRange[0]
            )
        return out



    def _buildTable(self, source):
        """
        Build a lookup table based on class attributes and a given data source.
        """

        def resizeSequence(source, length):
            """
            Resize a data sequence. Shrinking is here more effective than expanding.
            """
            sourceLen = len(source)
            out = []
            for i in range(length):
                key = round(i * (sourceLen/length))
                if key >= sourceLen:
                    key = sourceLen-1

                out.append(source[key])
            return out


        # Resize morningSlope and eveningSlope
        source['morning'] = resizeSequence( source['morning'], self.config.morningSlopeDuration)
        source['evening'] = resizeSequence( source['evening'], self.config.eveningSlopeDuration)


        # Create table and default to nightflat
        table = [source['night']] * settings.Global.totalDataPoints

        for timeCode in range(self._userMorningSlope[0], self._userMorningSlope[1]):
            table[timeCode] = source['morning'][timeCode - self._userMorningSlope[0]]
            # print("morning %s > %s" % (timeCode, table[timeCode]))


        for timeCode in range(self._userEveningSlope[0], self._userEveningSlope[1]):
            table[timeCode] = source['evening'][timeCode - self._userEveningSlope[0]]
            # print("evening %s > %s" % (timeCode, table[timeCode]))

        for timeCode in range(self._userEveningSlope[2], self._userEveningSlope[3]):
            table[timeCode] = source['evening'][timeCode - self._userEveningSlope[2]]
            # print("evening %s > %s" % (timeCode, table[timeCode]))


        for timeCode in range(self._userMorningSlope[1], self._userEveningSlope[2]):
            table[timeCode] = source['day']
            # print("day %s > %s" % (timeCode, table[timeCode]))


        return table
