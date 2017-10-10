import time
from settings import minPerTimeCode


class TimeCode:
    'Handles timekeeping in timecodes'
    def __init__(self, *, superspeed=None):
        self._minPerTimeCode = minPerTimeCode
        self._dataPoints = (24*60) / self._minPerTimeCode
        self._superspeed = superspeed
        self._superspeedCounter = round(self._dataPoints * .37)
        self._code = self.make()
        self.update = False


    def get(self):
        'Get latest timecode'
        return self._code


    def sleep(self):
        'Sleep until next timecode'
        while not self.update():
            time.sleep(1)


    def tick(self):
        'Update current timecode and set update flag on new code'
        if self._code == self.make():
            self.update = False
        else:
            self.update = True


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

            self._code = ( (h*60) + m ) // self._minPerTimeCode
            return self._code


    def decode(self, code=None):
        'Return the timestring linked to a timecode'
        if code == None:
            code = self._code

        minutes = code * self._minPerTimeCode
        h = minutes // 60
        m = minutes % 60

        return "%02d:%02d" % (h,m)
