from time import localtime
from settings import minPerTimeCode


class TimeCode:
    'Handles timekeeping in timecodes'
    def __init__(self, superspeed=None):
        self._minPerTimeCode = minPerTimeCode
        self._dataPoints = round( (24*60) // minPerTimeCode )
        self._superspeed = superspeed
        self._superspeedCounter = round(self._dataPoints * .37)
        self._code = self.make()
        self.update = False


    def get(self):
        'Get latest timecode'
        return self._code


    def tick(self):
        'Update current timecode and set update flag on new code'
        if self._code == self.make():
            self.update = False
        else:
            self.update = True


    def make(self, h=None, m=None, s=None):
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
                h = localtime().tm_hour
            if (m == None):
                m = time.localtime().tm_min
            if (s == None):
                s = time.localtime().tm_sec
            if isinstance(h, tuple):
                m = h[1]
                if len(h) > 2:
                    s = h[2]
                h = h[0]

            self._code = math.floor( ( (h*60) + m + (s/60) ) // self._minPerTimeCode )
            return self._code


    def decode(self, code=None):
        'Return the timestring associated with a timecode'
        if code is None:
            code = self._code

        minutes = code * self._minPerTimeCode
        h = math.floor(minutes / 60)
        m = math.floor(minutes % 60)
        s = math.floor( (minutes % 1) * 60 )

        return "%02d:%02d:%02d" % (h,m,s)
