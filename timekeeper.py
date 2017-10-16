import time
import math
import settings


class TimeKeeper:
    """
    Handles timekeeping in timecodes
    """
    def __init__(self):
        self._minPerTimeCode = settings.minPerTimeCode
        self.timeCode = self.makeCode()
        self.update = False


    def tick(self):
        """
        Progress the timekeeper and set update flag on timeCode change.
        """
        if self.timeCode == self.makeCode():
            self.update = False
        else:
            self.update = True


    def makeCode(self, h=0, m=0, s=0):
        """
        Calculate a new timecode
        """
        if h == 0 and m == 0 and s == 0:
            h = time.localtime().tm_hour
            m = time.localtime().tm_min
            s = time.localtime().tm_sec
        if type(h) is tuple:
            if len(h) > 2:
                s = h[2]
            m = h[1]
            h = h[0]

        self.timeCode = math.floor( ( (h*60) + m + (s/60) ) // settings.minPerTimeCode )
        return self.timeCode


    # def periodToCode(self, h=0, m=0, s=0):
    #     minutes = h*60 + m + s/60
    #
    #     return round( m // settings.minPerTimeCode )


    def timeStamp(self, code=None):
        """
        Return the timestring linked to a timecode
        """
        if code is None:  code = self.timeCode

        minutes = code * settings.minPerTimeCode
        h = math.floor(minutes / 60)
        m = math.floor(minutes % 60)
        s = math.floor( (minutes % 1) * 60 )

        return "%02d:%02d:%02d" % (h,m,s)
