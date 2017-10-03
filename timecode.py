import time
import math


class TimeCode:
    'Handles timekeeping in timecodes'
    def __init__(self, *, superspeed=None, minPerTimeCode=1):
        self._minPerTimeCode = minPerTimeCode
        self._dataPoints = (24*60) / self._minPerTimeCode
        self._superspeed = superspeed
        self._superspeedCounter = round(self._dataPoints * .37)
        self._code = self.make()

    def __del__(self):
        print("[Timecode] Garbage collection")


    def get(self):
        'Get latest timecode'
        return self._code


    def sleep(self):
        'Sleep until next timecode'
        while not self.update():
            time.sleep(1)


    def update(self):
        'Update current timecode and return a changed flag'
        if self._code == self.make():
            return False
        else:
            return True


    def make(self, h=None, m=None):
        'Calculate a new timecode'
        if(self._superspeed != None):
            # Superspeed mode for devellopment
            self._superspeedCounter += 1
            c = int( self._superspeedCounter / self._superspeed )
            if (c >= self._dataPoints):
                c = 0
                self._superspeedCounter = 0

            self._code = c
            return self._code
        else:
            # Normal realtime mode
            if (h == None):
                h = time.localtime().tm_hour
            if (m == None):
                m = time.localtime().tm_min
            if isinstance(h, tuple):
                m = h[1]
                h = h[0]

            self._code = math.floor( ( (h*60) + m ) / self._minPerTimeCode )
            return self._code

    def decode(self, code=None):
        'Return the timestring linked to a timecode'
        if code == None:
            code = self._code

        minutes = code * self._minPerTimeCode
        h = math.floor(minutes / 60)
        m = math.floor(minutes % 60)

        return "%02d:%02d" % (h,m)
