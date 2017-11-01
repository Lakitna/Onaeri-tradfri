# Alarm time (morning)
userAlarmTime    = (9, 0)       # Time alarm is set in (hour, minute)
userAlarmOffset  = 30           # Wakeup phase offset in minutes

# Bed time (evening)
userSleepTime    = (23, 30)     # Bedtime in (hour, minute)
userWindDownTime = 30           # Wind down time before bed in minutes


# Brightness and color tweaks
briCorrect       = (0, 100)     # [min, max] brightness in %
colorCorrect     = (0, 100)     # [min, max] color temp in %


# Cycle anatomy settings
morningSlopeDuration = 60       # Duration of morningslope in minutes
eveningSlopeDuration = 500      # Duration of eveningslope in minutes


# How to treat the lamp
automaticStateChange = True     # Allow the controller to automatically turn the lamps on/off


deviationDuration = 10          # Temporary cycle deviation duration in minutes
