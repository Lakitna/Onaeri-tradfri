from timekeeper import TimeKeeper
import control
import time
import settings


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
        self.brightness = self._buildTable(settings.app.brightnessData, self.config.briCorrect)
        self.color = self._buildTable(settings.app.colorData, self.config.colorCorrect)

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
                * (settings.app.briRange[1] - settings.app.briRange[0])
                + settings.app.briRange[0]
            )
        color = round(
                (self.color[timeCode] / 100)
                * (settings.app.colorRange[1] - settings.app.colorRange[0])
                + settings.app.colorRange[0]
            )

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

        def resizeSequence(source, length):
            """
            Crude way of resizing a data sequence. Shrinking is here more accurate than expanding.
            """
            sourceLen = len(source)
            out = []
            for i in range(length):
                key = round(i * (sourceLen/length))
                if key >= sourceLen:
                    key = sourceLen-1

                out.append(source[key])
            return out

        def applySourceRange(val):
            """
            Apply sourceRange to input.
            """
            ret = round(
                    val
                    * ((sourceRange[1] - sourceRange[0]) / 10)
                    + sourceRange[0]
                ) / 10

            if (ret % 1) == 0:
                ret = round(ret)

            return ret


        # Resize morningSlope and eveningSlope
        source['morning'] = resizeSequence( source['morning'], self.config.morningSlopeDuration)
        source['evening'] = resizeSequence( source['evening'], self.config.eveningSlopeDuration)


        # Create table and default to nightflat
        table = [source['night']+sourceRange[0]] * settings.app.totalDataPoints

        for timeCode in range(self._userMorningSlope[0], self._userMorningSlope[1]):
            table[timeCode] = applySourceRange(
                                    source['morning'][timeCode - self._userMorningSlope[0]]
                                )
            # print("morning %s > %s" % (timeCode, table[timeCode]))


        for timeCode in range(self._userEveningSlope[0], self._userEveningSlope[1]):
            table[timeCode] = applySourceRange(
                                    source['evening'][timeCode - self._userEveningSlope[0]]
                                )
            # print("evening %s > %s" % (timeCode, table[timeCode]))

        for timeCode in range(self._userEveningSlope[2], self._userEveningSlope[3]):
            table[timeCode] = applySourceRange(
                                    source['evening'][timeCode - self._userEveningSlope[2]]
                                )
            # print("evening %s > %s" % (timeCode, table[timeCode]))


        for timeCode in range(self._userMorningSlope[1], self._userEveningSlope[2]):
            table[timeCode] = applySourceRange( source['day'] )
            # print("day %s > %s" % (timeCode, table[timeCode]))


        return table
