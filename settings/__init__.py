import os
import importlib
from settings import app
import helper


def get(settingFile=""):
    """
    Return correct setting file
    """
    files = _settingFileList()
    if not settingFile in files:
        settingFile = "Default"
    userSettings = importlib.import_module(__name__+"."+settingFile, package=None)


    # Some calculations on settings
    userSettings.eveningSlopeDuration = round(userSettings.eveningSlopeDuration // app.minPerTimeCode)
    userSettings.morningSlopeDuration = round(userSettings.morningSlopeDuration // app.minPerTimeCode)


    # Make sure all settings are within expectations
    integrityValidation(userSettings)

    return userSettings


def _settingFileList():
    ret = []
    files = [f for f in os.listdir(__name__) if os.path.isfile(os.path.join(__name__, f))]
    for f in files:
        if f.endswith(app.settingFileExtention) and not f.startswith("_"):
            ret.append( f.split(".")[0] )
    return ret





def integrityValidation(userSettings):
    """
    Check integrity of settings
    """
    cycleName = userSettings.__name__.split(".")[1]
    print("Validating user settings for %s: " % cycleName, end='', flush=True)
    _checkIntegrity(userSettings.userAlarmTime, check="time")
    _checkIntegrity(userSettings.userAlarmOffset, check="unsigned")
    _checkIntegrity(userSettings.userSleepTime, check="time")
    _checkIntegrity(userSettings.userWindDownTime, check="unsigned")
    _checkIntegrity(userSettings.briCorrect, 0, 100)
    _checkIntegrity(userSettings.colorCorrect, 0, 100)
    _checkIntegrity(userSettings.morningSlopeDuration, check="unsigned")
    _checkIntegrity(userSettings.eveningSlopeDuration, check="unsigned")
    print("Done")




def _checkIntegrity(val, rmin=0, rmax=1, *, check=None):
    """
    Check value range and exit() on problems.
    """
    def _ruling(v, rnge):
        if not helper.inRange(v, rnge):
            print("[Settings] Invalid input '%s' for allowed range %s." % (v, rnge))
            exit()


    if check is None:
        if type(val) is dict or type(val) is list or type(val) is tuple:
            # If checking an iterable var:
            for v in val:
                _ruling(v, (rmin, rmax))
        else:
            _ruling(val, (rmin, rmax))

    elif check is "unsigned":
        if not val >= 0:
            print("[Settings] Invalid input '%s' for allowed range 0-infinite." % (val))
            exit()

    elif check is "time":
        _ruling(val[0], (0, 23))
        _ruling(val[1], (0, 59))

    else:
        print("[Settings] Check `%s` could not be performed." % check)
        exit()




print("Validating global settings: ", end='', flush=True)
_checkIntegrity(app.minPerTimeCode, check="unsigned")
_checkIntegrity(app.brightnessData['morning'], 0, 100)
_checkIntegrity(app.brightnessData['evening'], 0, 100)
_checkIntegrity(app.brightnessData['day'], 0, 100)
_checkIntegrity(app.brightnessData['night'], 0, 100)
_checkIntegrity(app.colorData['morning'], 0, 100)
_checkIntegrity(app.colorData['evening'], 0, 100)
_checkIntegrity(app.colorData['day'], 0, 100)
_checkIntegrity(app.colorData['night'], 0, 100)
_checkIntegrity(app.transitionTime, check="unsigned")
_checkIntegrity(app.briRange, 1, 254)
_checkIntegrity(app.colorRange, 2200, 4000)
_checkIntegrity(app.totalDataPoints, check="unsigned")
print("Done")
