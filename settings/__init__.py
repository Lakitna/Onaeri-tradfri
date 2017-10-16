import os
import importlib


def get(settingFile):
    """
    Return correct setting file
    """
    def _settingFileList():
        ret = []
        files = [f for f in os.listdir(__name__) if os.path.isfile(os.path.join(__name__, f))]
        for f in files:
            if f.endswith(".py") and not f.startswith("_"):
                ret.append( f.split(".")[0] )
        return ret


    files = _settingFileList()
    if not settingFile in files:
        settingFile = "Default"
    settings = importlib.import_module(__name__+"."+settingFile, package=None)

    # Make sure all settings are within expectations
    integrityValidation(settings)

    return settings



def integrityValidation(settings):
    # Check integrity of settings
    print("Validating global settings: ", end='', flush=True)
    _checkIntegrity(Global.minPerTimeCode, check="unsigned")
    _checkIntegrity(Global.brightnessData['morning'], 0, 100)
    _checkIntegrity(Global.brightnessData['evening'], 0, 100)
    _checkIntegrity(Global.brightnessData['day'], 0, 100)
    _checkIntegrity(Global.brightnessData['night'], 0, 100)
    _checkIntegrity(Global.colorData['morning'], 0, 100)
    _checkIntegrity(Global.colorData['evening'], 0, 100)
    _checkIntegrity(Global.colorData['day'], 0, 100)
    _checkIntegrity(Global.colorData['night'], 0, 100)
    _checkIntegrity(Global.transitionTime, check="unsigned")
    _checkIntegrity(Global.briRange, 1, 254)
    _checkIntegrity(Global.colorRange, 0, 13)
    _checkIntegrity(Global.colorValues, 2200, 4000)
    _checkIntegrity(Global.totalDataPoints, check="unsigned")
    print("Done")
    print("Validating user settings: ", end='', flush=True)
    _checkIntegrity(settings.briCorrect, 0, 100)
    _checkIntegrity(settings.colorCorrect, 0, 100)
    _checkIntegrity(settings.userAlarmTime, check="time")
    _checkIntegrity(settings.userAlarmOffset, check="unsigned")
    _checkIntegrity(settings.userSleepTime, check="time")
    _checkIntegrity(settings.userWindDownTime, check="unsigned")
    _checkIntegrity(settings.morningSlopeDuration, check="unsigned")
    _checkIntegrity(settings.eveningSlopeDuration, check="unsigned")
    print("Done")





def _checkIntegrity(val, rmin=0, rmax=1, *, check=None):
    'Check value range and exit() on problems.'
    def _ruling(x, mi, ma):
        if not mi <= x <= ma:
            # If not within range:
            print("[Settings] Invalid input '%s' for allowed range %d-%d." % (x, mi, ma))
            exit()


    if check is None:
        # If no special check:
        if type(val) is dict or type(val) is list or type(val) is tuple:
            # If checking an iterable var:
            for v in val:
                _ruling(v, rmin, rmax)
        else:
            # If not iterable:
            _ruling(val, rmin, rmax)

    elif check is "unsigned":
        # If requiring a unsigned value:
        if not val > 0:
            print("[Settings] Invalid input '%s' for allowed range 0-infinite." % (val))
            exit()

    elif check is "time":
        # If checking a timestamp:
        _ruling(val[0], 0, 23)
        _ruling(val[1], 0, 59)
