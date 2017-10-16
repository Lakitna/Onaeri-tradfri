#################
# Time settings #
#################
# Alarm time (morning)
userAlarmTime    = (6, 30)      # Time alarm is set in (hour, minute)
userAlarmOffset  = 30           # Wakeup phase offset in minutes

# Bed time (evening)
userSleepTime    = (22, 0)      # Bedtime in (hour, minute)
userWindDownTime = 30           # Wind down time before bed in minutes


# Brightness and color tweaks
briCorrect       = (0, 100)     # [min, max] brightness in %
colorCorrect     = (0, 100)     # [min, max] color temp in %


# Cycle anatomy settings
morningSlopeDuration = 60       # Duration of morningslope in minutes
eveningSlopeDuration = 500      # Duration of eveningslope in minutes






# Calculated settings
from settings import Global
eveningSlopeDuration = round(eveningSlopeDuration // Global.minPerTimeCode)
morningSlopeDuration = round(morningSlopeDuration // Global.minPerTimeCode)
