import os
import importlib
from settings import Global
import helper

blacklist = ["Global", "Template", "__init__"]

def _settingFileList():
    """
    Get list of setting files from settings folder.
    """
    ret = []
    files = [f for f in os.listdir(__name__) if os.path.isfile(os.path.join(__name__, f))]
    for f in files:
        if f.endswith(Global.settingFileExtention):
            f = f.split(".")[0] # Remove extention
            if f not in blacklist:
                ret.append( f )
    return ret

cycles = _settingFileList();
if len(cycles) == 0:
    helper.printError("No setting files found. Please create a file in the `settings` folder using the template.")
    exit()




def get(settingFile=""):
    """
    Return correct setting file
    """
    if not settingFile in cycles:
        helper.printError("Setting file %s not found" % settingFile)
        exit()
        
    userSettings = importlib.import_module(__name__+"."+settingFile, package=None)


    # Some calculations on settings
    userSettings.eveningSlopeDuration = round(userSettings.eveningSlopeDuration // Global.minPerTimeCode)
    userSettings.morningSlopeDuration = round(userSettings.morningSlopeDuration // Global.minPerTimeCode)
    userSettings.deviationDuration = round(userSettings.deviationDuration // Global.minPerTimeCode)


    # Make sure all settings are within expectations
    integrityValidation(userSettings)

    return userSettings




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
    _checkIntegrity(userSettings.deviationDuration, check="unsigned")
    helper.printDone()




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
_checkIntegrity(Global.colorRange, 2200, 4000)
_checkIntegrity(Global.totalDataPoints, check="unsigned")
_checkIntegrity(Global.deviationData, 0, 100)
helper.printDone()
