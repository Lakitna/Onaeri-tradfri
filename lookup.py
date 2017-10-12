import timecode
import control
import time
import settings


class Lookup:
    'Calculates and dispenses lookup tables for light values'
    def __init__(self):
        print("Building lookup table: ", end="")

        # Make a timecode object to calculate timecodes later
        tc = timecode.TimeCode();

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
        self._userAlarmOffset = round(
                settings.userAlarmOffset \
                // settings.minPerTimeCode
            )

        self._userSleepTime = tc.make( settings.userSleepTime )
        self._userWindDownTime = round(
                settings.userWindDownTime \
                // settings.minPerTimeCode
            )

        # Create morning and evening slopes based on sleep rhythm self._settings
        self._userMorningSlope = [0,0]
        self._userMorningSlope[0] = self._userAlarmTime - self._userAlarmOffset
        self._userMorningSlope[1] = self._userMorningSlope[0] \
                                    + settings.morningSlopeDuration

        self._userEveningSlope = [0,0,0,0]
        self._userEveningSlope[0] = self._userSleepTime \
                                    - settings.eveningSlopeDuration
        self._userEveningSlope[1] = self._userSleepTime
        self._userEveningSlope[2] = self._userEveningSlope[0]
        if self._userEveningSlope[0] < 0:
            self._userEveningSlope[2] += settings.totalDataPoints
            self._userEveningSlope[3] = settings.totalDataPoints
            self._userEveningSlope[0] = 0


        # Build brightness lookup table based on brightnessData and user self._settings
        self.brightness = self._buildTable(settings.brightnessData)

        # Build color lookup table based on colorData and user self._settings
        self.color = self._buildTable(settings.colorData)

        print("Done")
        # print(self.brightness)
        # print()
        # print(self.color)

    def setState(self, code, lightIndex):
        'Set lamp on/off state based on timecode'
        if code == self._userAlarmTime - self._userAlarmOffset:
            control.state(True, lightIndex)
            time.sleep(1)
            return True

        if code == self._userSleepTime:
            control.state(False, lightIndex)
            time.sleep(1)
            return True

        return False



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



    def _buildTable(self, source):
        'Build a lookup table based on settings and a given data source'
        def resize(src, length):
            'Resize a data sequence, shrinking is more effective than expanding'
            srcLen = len(src)

            out = []
            for i in range(length):
                x = round(i * (srcLen/length) )
                if x >= srcLen:
                    x = srcLen-1

                out.append(src[x])
            return out


        # Some vars for eveningSlope 0 hour rollover functionality
        eveningTotal = settings.eveningSlopeDuration
        eveningRolloverOffset = self._userEveningSlope[1] - self._userEveningSlope[0]

        # Resize morningSlope
        source['morning'] = resize( source['morning'], settings.morningSlopeDuration)
        # Resize eveningSlope
        source['evening'] = resize( source['evening'], eveningTotal)

        # Create data holder for lookup table
        table = []
        # Make a counter for eveningSlope
        eveningCodeCounter = 0
        for code in range(settings.totalDataPoints):
            # For every timecode in lookup table do:
            if self._userMorningSlope[0] <= code < self._userMorningSlope[1]:
                # If morningSlope:
                data = source['morning']
                table.append( data[code - self._userMorningSlope[0]] )
                # print('%s\tmorning %s\t%s' % (code, code - self._userMorningSlope[0], data[code - self._userMorningSlope[0]]))
                continue


            elif self._userEveningSlope[0] <= code < self._userEveningSlope[1]:
                # If eveningSlope (0 hour rollover):
                data = source['evening']
                table.append( data[eveningTotal - eveningRolloverOffset + eveningCodeCounter] )
                # print('%s\tevening %s\t%s' % (code, eveningTotal-length+eveningCodeCounter, data[eveningTotal-length+eveningCodeCounter]))

                eveningCodeCounter += 1
                continue

            elif self._userEveningSlope[2] <= code <= self._userEveningSlope[3]:
                # If eveningSlope (no rollover):
                data = source['evening']
                table.append( data[eveningCodeCounter - eveningRolloverOffset] )
                # print('%s\tevening %s\t%s' % (code, eveningCodeCounter-rolloverOffset, data[eveningCodeCounter-rolloverOffset]))

                eveningCodeCounter += 1
                continue


            elif self._userMorningSlope[1] <= code < self._userEveningSlope[2]:
                # If dayFlat:
                table.append( source['day'] )
                # print('%s\tday %s\t%s' % (code, 0, data))
                continue

            else:
                # Else it's night:
                table.append( source['night'] )
                # print('%s\tnight %s\t%s' % (code, 0, data))
                continue

        return table
