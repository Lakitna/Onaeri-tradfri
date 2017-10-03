import timecode
import control
import time
import settings


class Lookup:
    'Calculates and dispenses lookup tables for light values'
    def __init__(self):
        # Make a timecode object to calculate timecodes later
        tc = timecode.TimeCode(minPerTimeCode=settings.minPerTimeCode);

        # Calculate the limits of brightness and color based on self._settings
        self.briLimit = [0,0]
        self.briLimit[0] = round(
                (settings.briCorrect[0] / 100)
                * (settings.briRange[1] - settings.briRange[0])
                + settings.briRange[0]
            )
        self.briLimit[1] = round(
                (settings.briCorrect[1] / 100)
                * (settings.briRange[1] - settings.briRange[0])
                + settings.briRange[0]
            )

        self.colorLimit = [0,0]
        self.colorLimit[0] = round(
                (settings.colorCorrect[0] / 100)
                * (settings.colorRange[1] - settings.colorRange[0])
                + settings.colorRange[0]
            )
        self.colorLimit[1] = round(
                (settings.colorCorrect[1] / 100)
                * (settings.colorRange[1] - settings.colorRange[0])
                + settings.colorRange[0]
            )

        # Apply offset and sleep rhythm self._settings
        self._userAlarmTime = tc.make(settings.userAlarmTime)
        self._userAlarmOffset = settings.userAlarmOffset \
                                // settings.minPerTimeCode

        self._userSleepTime = tc.make( settings.userSleepTime )
        self._userWindDownTime = settings.userWindDownTime \
                                // settings.minPerTimeCode

        # Create morning and evening slopes based on sleep rhythm self._settings
        self._userMorningSlope = [0,0]
        self._userMorningSlope[0] = self._userAlarmTime - self._userAlarmOffset
        self._userMorningSlope[1] = self._userMorningSlope[0] \
                                    + (settings.morningSlope[1] - settings.morningSlope[0])

        self._userEveningSlope = [0,0,0,0]
        self._userEveningSlope[0] = self._userSleepTime \
                                    - (settings.eveningSlope[1] - settings.eveningSlope[0])
        self._userEveningSlope[1] = self._userSleepTime
        self._userEveningSlope[2] = self._userEveningSlope[0]
        self._userEveningSlope[3] = self._userEveningSlope[1]
        if self._userEveningSlope[0] < 0:
            self._userEveningSlope[2] += settings.totalDataPoints
            self._userEveningSlope[3] += settings.totalDataPoints


        # Build brightness lookup table based on brightnessData and user self._settings
        self.brightness = []
        for code in range(settings.totalDataPoints):
            self.brightness.append( settings.brightnessData[ self._shift(code) ] )

        # Build color lookup table based on colorData and user self._settings
        self.color = []
        for code in range(settings.totalDataPoints):
            self.color.append( settings.colorData[ self._shift(code) ] )


        # print(self.brightness)
        # print()
        # print(self.color)

    def setState(self, code):
        'Set lamp on/off state based on timecode'
        if code == self._userAlarmTime - self._userAlarmOffset:
            control.state(True)
            time.sleep(1)

        if code == self._userSleepTime:
            control.state(False)
            time.sleep(1)


    def get(self, code):
        'Get the values associated with timecode'
        bri = round(
                (self.brightness[code] / 100)
                * (self.briLimit[1] - self.briLimit[0])
                + self.briLimit[0]
            )
        col = round(
                (self.color[code] / 100)
                * (self.colorLimit[1] - self.colorLimit[0])
                + self.colorLimit[0]
            )
        return (bri, col)



    def _shift(self, code):
        # Ingest a timecode and return a shifted one based on user self._settings
        if self._userMorningSlope[0] <= code and code <= self._userMorningSlope[1]:
            # Morning slope
            return settings.morningSlope[0] + (code - self._userMorningSlope[0])

        if self._userEveningSlope[0] <= code and code <= self._userEveningSlope[1]:
            # Evening slope
            return settings.eveningSlope[0] + (code - self._userEveningSlope[0])

        if self._userEveningSlope[2] <= code and code <= self._userEveningSlope[3]:
            # Evening slope with 0 hour rollover
            return settings.eveningSlope[0] + (code - self._userEveningSlope[2])

        if self._userMorningSlope[1] < code and code < self._userEveningSlope[2]:
            # Day flat
            return settings.dayFlat

        # Night flat or fallback
        return settings.nightFlat
