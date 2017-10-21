# Alarm time (morning)
userAlarmTime    = (8, 0)       # Time alarm is set in (hour, minute)
userAlarmOffset  = 0            # Wakeup phase offset in minutes

# Bed time (evening)
userSleepTime    = (22, 0)      # Bedtime in (hour, minute)
userWindDownTime = 0            # Wind down time before bed in minutes


# Brightness and color tweaks
briCorrect       = (10, 90)     # [min, max] brightness in %
colorCorrect     = (0, 0)       # [min, max] color temp in %


# Cycle anatomy settings
morningSlopeDuration = 60       # Duration of morningslope in minutes
eveningSlopeDuration = 400      # Duration of eveningslope in minutes


# How to treat the lamp
automaticStateChange = False    # Allow the controller to automatically turn the lamps on/off
